"""
retriever_tool.py

- single BFS + spanning-tree implementation
- modular DB, graph, fetcher, search
- DRY SQL templates
- context managers for safety
"""
import os, json, re, logging, struct
from collections import defaultdict, deque
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple, Set, Type
import math
import pyodbc
import pandas as pd
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.identity import ClientSecretCredential, AzureCliCredential
from pydantic import BaseModel, Field, PrivateAttr
from src.models.intermediate_step import IntermediateStep
from src.models.tool import ToolArtifact
from src.core.base import LamBotTool
from src.models.constants import ToolType
from src.models.base import ConfiguredBaseModel
from src.clients import LifespanClients
from src.core.tools.community.nce_chatbot_pipeline.openai_config import llm_4o
from .prompts import prompts
from collections import defaultdict
from datetime import datetime

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------
class TextField(BaseModel):
    iqms_id: str
    parent_id: Optional[str]
    project: str
    part_number: str
    related_records: List[str]
    text_blob: str
    url: str


class FastToolSpec(ConfiguredBaseModel):
    tool_name: str = Field(..., desc="Name of the tool.")
    tool_description: str = Field(..., desc="Description of the tool.")
    top_k: int = Field(..., desc="# Azure Search hits." )
    prompts: Dict[str, Tuple[str, str]] = Field(
        default_factory=dict,
        desc="Prompt overrides."
    )


class ToolInput(BaseModel):
    query: str = Field(..., desc="Seed IQMS ID or part number.")


# -----------------------------------------------------------------------------
# DBClient: manage connections/cursors
# -----------------------------------------------------------------------------
class DBClient:
    def __init__(self):
        self.server   = os.getenv("FABRIC_SERVER")
        self.database = "lhg_glb"
        self.driver   = "ODBC Driver 17 for SQL Server"

        # Service-principal credentials
        self.client_id     = os.getenv("FABRIC_CLIENT_ID")
        self.client_secret = os.getenv("FABRIC_CLIENT_SECRET")
        self.tenant_id     = os.getenv("FABRIC_TENANT_ID")

    @contextmanager
    def connect(self):
        # 1) Force TCP + port
        server = f"tcp:{self.server},1433"

        # 2) Build a *basic* connection string (no Authentication=... flag)
        conn_str = (
            f"Driver={{{self.driver}}};"
            f"Server={server};"
            f"Database={self.database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )

        # 3) Pick and call the credential
        if all((self.client_id, self.client_secret, self.tenant_id)):
            credential = ClientSecretCredential(
                tenant_id     = self.tenant_id,
                client_id     = self.client_id,
                client_secret = self.client_secret
            )
            scope = "https://database.windows.net/.default"
        else:
            credential = AzureCliCredential()
            scope = "https://database.windows.net/.default"

        # 4) Fetch AAD access token
        token = credential.get_token(scope).token
        token_bytes = token.encode("utf-8")

        # 5) Wrap into the SQL Server-specific blob
        exptoken = b"".join(bytes([b]) + b"\x00" for b in token_bytes)
        token_struct = struct.pack("=i", len(exptoken)) + exptoken
        SQL_COPT_SS_ACCESS_TOKEN = 1256

        # 6) Connect, passing the token via attrs_before
        conn = pyodbc.connect(
            conn_str,
            attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}
        )

        try:
            yield conn
        finally:
            conn.close()

# -----------------------------------------------------------------------------
# GraphBuilder: unified BFS + spanning-tree
# -----------------------------------------------------------------------------
class GraphBuilder:
    """
    BFS over IQMS graph in Azure Fabric tables.
    Skips invalid IDs: None, '', '-1'.
    """
    # table/view names, project label, whether it has a real related‐records column
    VIEWS: List[Tuple[str, str, bool]] = [
        ("[lhg_glb].[quality].[rpt_nce_legacy]",  "NCe",  False),
        ("[lhg_glb].[quality].[rpt_mrbe_legacy]", "MRBe", False),
        ("[lhg_glb].[quality].[rpt_8d_legacy]",   "8D",   True),
    ]

    # IDs to ignore entirely
    INVALID_IDS = {None, "", "-1"}

    # SQL template with placeholders
    SQL_FETCH_TEMPLATE = """
    SELECT
      [iqms_id],
      [parent_id],
      {rel_column}   AS related_records,
      '{src}'        AS source
    FROM {view}
    WHERE
      ( [iqms_id] = ?
      OR [parent_id] = ?
        {like_clause}
      )
      {date_clause}
      {rev_clause}     
    """

    def __init__(self, db_client):
        self.db = db_client
        # for splitting comma-lists in related_records
        self._related_splitter = re.compile(r"\s*,\s*")

    def _to_param(self, val: str):
        """
        Convert a digit-only string to int, else leave as str.
        """
        if isinstance(val, str) and val.isdigit():
            return int(val)
        return val

    def _parse_related(self, cell) -> Set[str]:
        """
        Given a CSV‐style field, split on commas.
        Returns an empty set if cell is None/empty.
        """
        if not cell:
            return set()
        return set(self._related_splitter.split(str(cell).strip()))


    def bfs_traverse(
        self,
        seeds: List[str],
        start_dt: Optional[datetime]    = None,
        end_dt:   Optional[datetime]    = None,
        part_revs: Optional[List[str]]  = None
    ) -> Tuple[Dict[str, Set[Tuple[str,str]]], Set[str]]:
        """
        BFS over IQMS graph, optionally filtering date_opened and—
        for NCe only—part_rev ∈ part_revs.
        """
        # prebuild filters
        date_clause, date_params = self._build_date_filter(start_dt, end_dt)
        rev_clause,  rev_params  = self._build_rev_filter(part_revs)

        adj     = defaultdict(set)
        visited = set()
        queue   = deque(seeds)

        with self.db.connect() as conn, conn.cursor() as cur:
            while queue:
                nid = queue.popleft()
                if nid in self.INVALID_IDS or nid in visited:
                    continue
                visited.add(nid)

                eqv, likev = self._to_param(nid), f"%{nid}%"

                for view, src, has_rel in self.VIEWS:
                    # 1) decide REL columns
                    rel_col, like_clause = self._rel_clauses(has_rel)

                    # 2) only NCe gets the rev‐clause
                    rev_src_clause = rev_clause if src == "NCe" else ""

                    # 3) assemble & run
                    sql = self.SQL_FETCH_TEMPLATE.format(
                        view        = view,
                        src         = src,
                        rel_column  = rel_col,
                        like_clause = like_clause,
                        date_clause = date_clause,
                        rev_clause  = rev_src_clause
                    ).replace("\n", " ")

                    params = self._view_params(
                        eqv, likev, has_rel,
                        date_params, src, rev_params
                    )

                    cur.execute(sql, params)
                    rows = cur.fetchall()

                    # 4) process results
                    self._process_db_rows(rows, adj, visited, queue)

        return adj, visited
    # bfs_traverse Helper: build related records filter clause
    def _rel_clauses(self, has_rel: bool) -> Tuple[str, str]:
        """Return (rel_column, like_clause) based on has_rel."""
        if has_rel:
            return (
                "CAST([related_records_8d] AS VARCHAR(100))",
                "OR [related_records_8d] LIKE ?"
            )
        return "NULL", ""
    # bfs_traverse Helper: builds parameter set for query
    def _view_params(
        self,
        eqv: str,
        likev: str,
        has_rel: bool,
        date_params: List[str],
        src: str,
        rev_params: List[str]
    ) -> List[str]:
        """Builds the parameter list for one view-query."""
        params = [eqv, eqv]
        if has_rel:
            params.append(likev)
        params.extend(date_params)
        if src == "NCe":
            params.extend(rev_params)
        return params

    def _process_db_rows(
        self,
        rows,
        adj: Dict[str, Set[Tuple[str,str]]],
        visited: Set[str],
        queue: deque
    ) -> None:
        """Add edges & enqueue new nodes for all fetched rows."""
        for child_id, parent_id, rel_csv, _ in rows:
            child = str(child_id).strip()
            if child in self.INVALID_IDS:
                continue

            parent = (
                str(parent_id).strip()
                if parent_id not in self.INVALID_IDS
                else None
            )

            # parent ↔ child
            if parent:
                adj[parent].add((child,  "parent"))
                adj[child].add((parent, "parent"))

            # related ↔ child
            related = self._parse_related(rel_csv)
            for r in related:
                adj[child].add((r, "related"))
                adj[r].add((child, "related"))

            # enqueue new neighbors
            neighbors = {child}
            if parent:
                neighbors.add(parent)
            neighbors |= set(related)

            for nbr in neighbors:
                if nbr not in visited and nbr not in self.INVALID_IDS:
                    queue.append(nbr)
    # ──────────────────────────────
    # bfs_traverse Helper: build the date filter clause + its params
    def _build_date_filter(
        self,
        start_dt: Optional[datetime],
        end_dt:   Optional[datetime]
    ) -> Tuple[str, List[str]]:
        if not start_dt:
            return "", []
        clause = "AND [date_opened] >= ?"
        params = [start_dt.date().isoformat()]
        if end_dt:
            clause += " AND [date_opened] <= ?"
            params.append(end_dt.date().isoformat())
        return clause, params

    # bfs_traverse Helper: build the NCe revision filter clause + its params
    def _build_rev_filter(
        self,
        part_revs: Optional[List[str]]
    ) -> Tuple[str, List[str]]:
        if not part_revs:
            return "", []
        placeholders = ",".join("?" for _ in part_revs)
        return f"AND [part_cur_rev] IN ({placeholders})", list(part_revs)

    def build_spanning_tree(
        self,
        adj: Dict[str, Set[Tuple[str,str]]],
        roots: List[str]
    ) -> Tuple[Dict[str, Optional[str]], Dict[str,str]]:
        parent: Dict[str, Optional[str]] = {r: None for r in roots}
        edge:   Dict[str, str]           = {r: ""   for r in roots}
        q = deque(roots)

        while q:
            u = q.popleft()
            for v, rel in sorted(adj.get(u, []), key=lambda x: x[0]):
                if v not in parent:
                    parent[v] = u
                    edge[v]   = rel
                    q.append(v)
        # ensure all keys/values are str(None) safe
        return ({str(k): (str(v) if v else None) for k, v in parent.items()},
                {str(k): rel for k, rel in edge.items()})

    def format_spanning_tree(
        self,
        records: List[TextField],
        tree_parent: Dict[str, Optional[str]],
        tree_edge:   Dict[str, str],
        root:        str
    ) -> str:
        """
        Render an ASCII tree from the BFS spanning-tree (tree_parent, tree_edge),
        marking edges of type "related" with a [related] tag.
        """
        # 1) map nodes
        rec_by_id = {r.iqms_id: r for r in records}

        # 2) build & sort children
        children = {nid: [] for nid in rec_by_id}
        for node, parent in tree_parent.items():
            if parent:
                children[parent].append(node)
        for lst in children.values():
            lst.sort()

        lines: List[str] = []

        def _print(node_id: str, prefix: str, is_last: bool):
            node = rec_by_id[node_id]
            conn = "└── " if is_last else "├── "
            tag  = " [related]" if tree_edge.get(node_id) == "related" else ""
            lines.append(
                f"{prefix}{conn}"
                f"{node_id} (P:{node.project}, PN:{node.part_number})"
                f"{tag}"
            )

            new_prefix = prefix + ("    " if is_last else "│   ")
            kids = children.get(node_id, [])
            parent_kids  = [k for k in kids if tree_edge.get(k)=="parent"]
            related_kids = [k for k in kids if tree_edge.get(k)=="related"]
            total = len(parent_kids) + len(related_kids)
            idx = 0

            for k in parent_kids:
                _print(k, new_prefix, idx == total - 1 and not related_kids)
                idx += 1
            for k in related_kids:
                _print(k, new_prefix, idx == total - 1)
                idx += 1

        # 3) seed
        root_rec = rec_by_id[root]
        lines.append(f"{root} (P:{root_rec.project}, PN:{root_rec.part_number})")
        first_children = children.get(root, [])
        for i, kid in enumerate(first_children):
            _print(kid, "", i == len(first_children) - 1)

        return "\n".join(lines)


# -----------------------------------------------------------------------------
# DetailFetcher: pull and normalize pandas DataFrame
# -----------------------------------------------------------------------------
class DetailFetcher:
    QUERIES = {
        "MRBe": """
            SELECT 
                "iqms_id",
                "date_opened", 
                "part_number", 
                "parent_id",
                "fa_priority", 
                "mrbe_comments_log",
                "title", 
                "description", 
                "disposition",
                "fa_finding_description", 
                "fa_summary", 
                "return_reason"
            FROM [lhg_glb].[quality].[rpt_mrbe_legacy]
            WHERE [iqms_id] IN ({ph})
        """,
        "8D":  """
            SELECT       
                "iqms_id", 
                "date_opened", 
                "part_number", 
                "parent_id",
                "related_records_8d" as "related_records",
                "investigation_group", 
                "investigation_group_detail",
                "8d_finding", 
                "8d_finding_details",
                "d3_summary", 
                "d4_summary", 
                "d5_summary",
                "d6_summary", 
                "d7_summary",
                "initial_problem_statement", 
                "final_problem_statement"
            FROM [lhg_glb].[quality].[rpt_8d_legacy]
            WHERE [iqms_id] IN ({ph})
        """,
        "NCe": """
            SELECT                     
                "iqms_id",
                "customer_name",
                "sap_damage_code_group",
			    "sap_damage_code",
                "date_opened",
                "part_number",
                "part_cur_rev",
                "parent_id",
                "escape_title",
                "title",
                "operation_short_text",
                "escape_description",
                "description"
            FROM [lhg_glb].[quality].[rpt_nce_legacy]
            WHERE [iqms_id] IN ({ph})
        """
    }

    def __init__(self, db_client: DBClient):
        self.db = db_client

    def fetch_details(self, ids: List[str]) -> pd.DataFrame:
        # 1) pull each project’s rows
        ph  = ",".join("?" for _ in ids)
        dfs = []
        with self.db.connect() as conn:
            for proj, sql in self.QUERIES.items():
                df = pd.read_sql(sql.format(ph=ph), conn, params=ids)
                df["project"] = proj
                dfs.append(df)

        # 2) concatenate
        df = pd.concat(dfs, ignore_index=True)

        # 3) normalize key columns
        df["iqms_id"]     = df["iqms_id"].astype(str).str.strip()
        df["parent_id"]   = (
            df["parent_id"]
              .astype(str)
              .replace({"nan": None})
        )
        df["part_number"] = df["part_number"].fillna("").astype(str)
        df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")

        # 4) build a clickable URL
        BASE_IQMS_URL = "https://trackwise.lamresearch.com/trackwise/Gateway.html?"
        df["url"] = BASE_IQMS_URL + df["iqms_id"]

        # 5) split out related_records (if present)
        if "related_records" in df.columns:
            df["related_records"] = (
                df["related_records"]
                  .fillna("")
                  .astype(str)
                  .str.split(r"\s*,\s*")
            )
        else:
            df["related_records"] = [[] for _ in range(len(df))]

        # 6) return **all** columns (raw + normalized)
        return df

# -----------------------------------------------------------------------------
# SearchClientFactory: load .env once
# -----------------------------------------------------------------------------
class SearchClientFactory:
    def __init__(self):
        load_dotenv()
        self.ep  = os.getenv("SEARCH_API_BASE", "").strip()
        self.key = os.getenv("SEARCH_API_KEY","").strip()
        self.api_version = os.getenv("SEARCH_API_VERSION")
        self.idx = "index-oai-failure-analysis-with-attachments-alias"
        if not all((self.ep, self.key)):
            raise ValueError("Missing Azure Search config in .env")
        if not self.ep.lower().startswith("http"):
            self.ep = "https://" + self.ep
        if "search.windows.net" not in self.ep.lower():
            self.ep = self.ep.rstrip("/") + ".search.windows.net"

    def get(self) -> SearchClient:
        return SearchClient(endpoint=self.ep, index_name=self.idx, credential=AzureKeyCredential(self.key), api_version=self.api_version)


# -----------------------------------------------------------------------------
# Prompt property mixin (unchanged)
# -----------------------------------------------------------------------------
def make_prompt_property(key: str):
    """
    Returns a property that:
      1) looks for an override in self._tool_spec.prompts[key]
      2) falls back to the module-level prompts[key]
      3) fetches the live prompt from Langfuse by name/label/fallback
      4) if anything goes wrong, returns the fallback text
    """
    def prop(self) -> str:
        # 1) override in tool-spec?
        entry = self._tool_spec.prompts.get(key)
        # 2) fallback in module-level prompts?
        if entry is None:
            entry = prompts.get(key)
        if entry is None:
            raise ValueError(f"No prompt entry found for key: {key}")

        prompt_name, fallback_text = entry

        # 3) fetch from Langfuse
        try:
            lf_client = LifespanClients.get_instance().langfuse_manager
            lf_prompt = lf_client.get_prompt(
                prompt_name=prompt_name,
                fallback_prompt=fallback_text
            )
            return lf_prompt

        # 4) on any failure, use the fallback
        except Exception as e:
            logger.warning(
                "Failed to fetch prompt %r from Langfuse (using fallback): %s",
                prompt_name, e,
                exc_info=True
            )
            return fallback_text

    return property(prop)

def add_prompt_properties(cls):
    for k in prompts:
        prop_name = k.lower()
        if not hasattr(cls, prop_name):
            setattr(cls, prop_name, make_prompt_property(k))
    return cls


# -----------------------------------------------------------------------------
# FastChatBotTool (orchestrator)
# -----------------------------------------------------------------------------
@add_prompt_properties
class FastChatBotTool(LamBotTool):
    args_schema: Type[ToolInput] = ToolInput
    _tool_spec: FastToolSpec    = PrivateAttr()
    _db_client: DBClient       = PrivateAttr()
    _graph: GraphBuilder       = PrivateAttr()
    _fetcher: DetailFetcher    = PrivateAttr()
    _search_fac: SearchClientFactory = PrivateAttr()

    def __init__(self, name, desc, spec: FastToolSpec, ttype: ToolType):
        super().__init__(name=name, description=desc, tool_type=ttype)
        self._tool_spec  = spec
        self._db_client  = DBClient()
        self._graph      = GraphBuilder(self._db_client)
        self._fetcher    = DetailFetcher(self._db_client)
        self._search_fac = SearchClientFactory()
    @classmethod
    def from_tool_spec(cls, spec: FastToolSpec):
        return cls(spec.tool_name, spec.tool_description, spec, ToolType.non_retriever_tool)

    def _extract_roots(
        self,
        text: str
    ) -> Tuple[List[str], Optional[datetime], Optional[datetime], List[str]]:
        """
        1) Force the LLM to call extract_roots(...) every time.
        2) Parse out:
             - iqms_id     : List[str]
             - part_number : List[str]
             - start_date  : Optional[YYYY-MM-DD]
             - end_date    : Optional[YYYY-MM-DD]
             - part_rev    : Optional[List[str]]
        3) Resolve part_numbers → IQMS IDs.
        4) Return (roots, start_dt, end_dt, part_revs).
        """
        EXTRACT_ROOTS_FN = {
            "name":        "extract_roots",
            "description": "Extract IQMS IDs, part_numbers, dates, part rev/revisions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "iqms_id": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "part_number": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "start_date": {
                        "type":   ["string", "null"],
                        "format": "date"
                    },
                    "end_date": {
                        "type":   ["string", "null"],
                        "format": "date"
                    },
                    "part_rev": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional filter for NCe part_rev"
                    }
                }
            }
        }

        # ── 1) Call the LLM, forcing the function call every time ──
        prompt = self.fast_get_roots_prompt.format(query=text)
        msg = llm_4o.invoke(
            prompt,
            functions=[EXTRACT_ROOTS_FN],
            function_call={ "name": EXTRACT_ROOTS_FN["name"] }
        )

        # ── 2) Unwrap the function_call payload ────────────────────
        func_call = getattr(msg, "function_call", None) \
                    or msg.additional_kwargs.get("function_call")
        if not func_call:
            raise ValueError("Expected extract_roots() function_call but got none")

        raw_args = (
            func_call.arguments
            if hasattr(func_call, "arguments")
            else func_call.get("arguments", "")
        )

        # ── 3) Parse the JSON ─────────────────────────────────────
        try:
            parsed = json.loads(raw_args)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON from extract_roots(): %s\n>>>%s", e, raw_args)
            raise ValueError("Could not parse JSON from LLM") from e

        # ── 4) Parse optional dates ────────────────────────────────
        def to_dt(s: Optional[str]) -> Optional[datetime]:
            return datetime.fromisoformat(s) if s else None

        start_dt = to_dt(parsed.get("start_date"))
        end_dt   = to_dt(parsed.get("end_date"))


        # ── 5) Build the IQMS‐ID roots list ────────────────────────
        roots: List[str] = []
        for iq in parsed.get("iqms_id", []):
            roots.append(str(iq).strip())
        
        for pn in parsed.get("part_number", []):
            pn_str = str(pn).strip()
            if pn_str:
                # pass the LLM-extracted date window into the part lookup
                roots.extend(self._find_by_part(pn_str, start_dt, end_dt))

        if not roots:
            raise ValueError("LLM extracted no IQMS IDs or part_numbers")


        # ── 6) Safely normalize part_rev into a List[str] ────────
        raw_revs = parsed.get("part_rev")
        if raw_revs is None:
            raw_revs = []
        elif not isinstance(raw_revs, list):
            # if the model returned a single string or number
            raw_revs = [raw_revs]

        part_revs: List[str] = [
            str(r).strip()
            for r in raw_revs
            if str(r).strip()
        ]

        return roots, start_dt, end_dt, part_revs
    
    def _find_by_part(
        self,
        partnum: str,
        start_dt: Optional[datetime] = None,
        end_dt:   Optional[datetime] = None
    ) -> List[str]:
        """
        Lookup IQMS_IDs by part number, optionally applying
        the same [date_opened] range filter that BFS uses.
        """
        comparator = "LIKE" if "%" in partnum else "="

        # 1) build date clauses & collect their params
        date_sql = ""
        date_params: List[str] = []
        if start_dt:
            date_sql += " AND [date_opened] >= ?"
            date_params.append(start_dt.date().isoformat())
        if end_dt:
            date_sql += " AND [date_opened] <= ?"
            date_params.append(end_dt.date().isoformat())

        # 2) assemble the UNION-ALL query (3 branches)
        sql = f"""
        SELECT TOP 10 [iqms_id]
        FROM (
          SELECT [iqms_id], [date_opened]
            FROM [lhg_glb].[quality].[rpt_mrbe_legacy]
           WHERE [part_number] {comparator} ? {date_sql}
          UNION ALL
          SELECT [iqms_id], [date_opened]
            FROM [lhg_glb].[quality].[rpt_8d_legacy]
           WHERE [part_number] {comparator} ? {date_sql}
          UNION ALL
          SELECT TOP 1 [iqms_id], [date_opened]
            FROM [lhg_glb].[quality].[rpt_nce_legacy]
           WHERE [part_number] {comparator} ? {date_sql}
           ORDER BY [date_opened] DESC
        ) AS combined
        ORDER BY combined.[date_opened] DESC
        """

        # 3) build the param list: one partnum + date_params per branch
        params: List = []
        for _ in range(3):
            params.append(partnum)
            params.extend(date_params)

        # 4) execute & collect
        with self._db_client.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, *params)
            ids = [str(r[0]).strip() for r in cur.fetchall()]

        if not ids:
            raise ValueError(f"No IDs found for part pattern '{partnum}'")
        return ids

    def _is_nullish(self, v) -> bool:
        """
        Return True if v is one of:
          - None
          - empty string
          - a float NaN
        """
        if v is None or v == "":
            return True
        # catch Python float NaN
        if isinstance(v, float) and math.isnan(v):
            return True
        return False

    def _clean_value(self, v):
        """
        Recursively clean nested dicts/lists.
        """
        if isinstance(v, dict):
            return self._clean_dict(v)
        if isinstance(v, list):
            cleaned = []
            for x in v:
                if not self._is_nullish(x):
                    cleaned.append(self._clean_value(x))
            return cleaned
        return v

    def _clean_dict(self, d: Dict) -> Dict:
        """
        Remove any keys from d whose value is nullish (None, "", NaN).
        """
        return {
            k: self._clean_value(v)
            for k, v in d.items()
            if not self._is_nullish(v)
        }

    def _run(self, query: str) -> str:
        try:
            # ── 1) Extract roots via LLM ─────────────────────────────────────
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(message="Extracting Roots")
            )
            roots, start_dt, end_dt, part_revs = self._extract_roots(query)

            # ── 1.a) Date filter notice ─────────────────────────────────────
            if start_dt:
                label = f"{start_dt.date()}"
                label = f"{label} to {end_dt.date()}" if end_dt else f"since {label}"
                self.dispatch_intermediate_step(
                    intermediate_step=IntermediateStep(
                        message=f"Applying time filter {label}"
                    )
                )

            # ── 1.b) Part-rev filter notice ─────────────────────────────────
            if part_revs:
                rev_label = ", ".join(part_revs)
                self.dispatch_intermediate_step(
                    intermediate_step=IntermediateStep(
                        message=f"Applying part-rev filter: {rev_label}"
                    )
                )

            # ── 2) BFS traverse the IQMS graph ────────────────────────────────
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(message="Traversing Graph BFS")
            )
            adj, visited = self._graph.bfs_traverse(
                seeds     = roots,
                start_dt  = start_dt,
                end_dt    = end_dt,
                part_revs = part_revs
            )

            # ── 3) Fetch all record details into a DataFrame ─────────────────
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(message="Fetching Record Details")
            )
            df = self._fetcher.fetch_details(sorted(visited))

            # ── 4) Convert entire DataFrame → list of dicts (all columns!) ──
            records: List[dict] = df.to_dict(orient="records")

            # ── 5) Pull attachments from Azure Cognitive Search ─────────────
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(message="Fetching Attachments")
            )
            client   = self._search_fac.get()
            filter_q = f"search.in(iqms_id,'{','.join(sorted(visited))}',',')"
            results  = client.search(
                search_text="*",
                filter=filter_q,
                top=self._tool_spec.top_k
            )
            docs = list(results)

            # Bucket attachments by IQMS ID
            hits_by_id: Dict[str, List[Dict]] = defaultdict(list)
            for doc in docs:
                trimmed = {
                    k: doc.get(k)
                    for k in ["url", "file_name", "chunk", "category"]
                }
                iq = str(doc.get("iqms_id", "")).strip()
                if iq:
                    hits_by_id[iq].append(trimmed)

            # ── 6) Build nodes **agnostically** ──────────────────────────────
            instr = self.fast_instruction_prompt
            nodes: List[dict] = []
            for rec in records:
                node = rec.copy()
                # rename the primary key
                node["id"] = node.pop("iqms_id")
                # inject any attachments (empty list if none)
                node["attachments"] = hits_by_id.get(node["id"], [])
                #Remove empty Attributes in Node to simplify context
                clean_node = self._clean_dict(node)
                nodes.append(clean_node)

            # Build a lookup for projects when constructing edges
            rec_map = { node["id"]: node for node in nodes }

            # ── 7) Build unique edges with project context ───────────────────
            edges = []
            seen_edges = set()
            for src, neighbors in adj.items():
                if src not in rec_map:
                    continue
                for dst, rel in neighbors:
                    if dst not in rec_map:
                        continue
                    key = tuple(sorted((src, dst))) + (rel,)
                    if key in seen_edges:
                        continue
                    seen_edges.add(key)

                    raw_edge = {
                        "source":          src,
                        "source_project":  rec_map[src]["project"],
                        "target":          dst,
                        "target_project":  rec_map[dst]["project"],
                        "type":            rel
                    }
                    # Clean empty edges (should be rare) 
                    clean_edge = self._clean_dict(raw_edge)
                    edges.append(clean_edge)

            # Ensure isolated roots appear at least once
            for r in roots:
                if r in rec_map and not any(e["source"] == r for e in edges):
                    raw_edge = {
                        "source":         r,
                        "source_project": rec_map[r]["project"],
                        "target":         r,
                        "target_project": rec_map[r]["project"],
                        "type":           "root"
                    }
                    edges.append(self._clean_dict(raw_edge))

            # ── 9) Assemble JSON‐KG and dispatch ─────────────────────────────
            kg_payload = {
                "instructions": instr,
                "nodes":        nodes,
                "edges":        edges
            }
            kg_json = json.dumps(kg_payload, indent=2, default=str)

            # render as HTML artifact as well
            html = f"<pre style='font-family:monospace'>{kg_json}</pre>"
            self.dispatch_tool_artifact(
                ToolArtifact(
                    content      = html,
                    display_name = "Tool Response (Knowledge Graph)",
                    tool_name    = self.name
                )
            )
            
            # ── 10) Return raw JSON ────────────────────────────────────────
            return kg_json

        except ValueError as ve:
            logger.error("User error in FAST tool: %s", ve)
            return str(ve)

        except Exception as e:
            logger.exception("Unexpected failure in FAST tool")
            return f"FAST tool failed: {e}"


# -----------------------------------------------------------------------------
# Instantiate
# -----------------------------------------------------------------------------
spec = FastToolSpec(
    tool_name="bfs_retriever",
    tool_description="BFS-based iQMS retriever + Azure search",
    top_k=50
)
fast_retriever_tool = FastChatBotTool.from_tool_spec(spec)
