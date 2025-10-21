from langchain_core.documents import Document
from typing import Optional, Dict
from src.models.citation import CitationTagAliasSpec

class LamBotDocument(Document):
    """Class for storing page content (chunk), associated metadata, and an LLM context."""

    llm_context: str
    """The chunk of text that is relevant to the user question and will be passed to a language model in the tool response."""

    origin: Optional[str] = None
    """Name of the retriever tool from which this Document originated."""

    citation_field_mappings: Optional[Dict[str, CitationTagAliasSpec]] = {}
    """Mappings for citation fields, default is an empty dictionary."""

    def __str__(self) -> str:
        """Override __str__ to include page_content, metadata, llm_context, and origin."""
        base_str = super().__str__()
        context_str = str(self.llm_context) if self.llm_context else "None"
        origin_str = self.origin if self.origin else "None"
        citation_field_mappings_str = str(self.citation_field_mappings) if self.citation_field_mappings else "{}"
        return f"{base_str} llm_context={context_str} origin={origin_str} citation_field_mappings={citation_field_mappings_str}"
