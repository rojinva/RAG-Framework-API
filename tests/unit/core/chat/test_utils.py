import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "src"))
import pytest
from unittest.mock import patch 

import pytest

@pytest.fixture
def mock_inits_and_import_converters(mocker):
    with patch.dict('sys.modules', {
        'dotenv.load_dotenv': mocker.MagicMock(),
        'src.models.request': mocker.MagicMock(),
        'src.models.request.LamBotChatRequest': mocker.MagicMock(),
        'src.models.response': mocker.MagicMock(),
        'src.models.response.LamBotChatResponse': mocker.MagicMock(),
        'src.models.retriever_tool': mocker.MagicMock(),
        'src.models.security_data': mocker.MagicMock(),
        'src.core.retrievers': mocker.MagicMock(),
        'src.core.retrievers.retriever': mocker.MagicMock(),
        'src.core.retrievers.MultiRetriever': mocker.MagicMock(),
        "src.core.base": mocker.MagicMock(),
        'src.core.bots': mocker.MagicMock(),
        'src.core.bots.lambot': mocker.MagicMock(),
        'src.core.tools.common': mocker.MagicMock(),
        'src.core.utils.log_trace': mocker.MagicMock(),
        'src.core.chat.conversation_engine': mocker.MagicMock(),
        'src.core.chat.conversation_engine.ConversationEngine': mocker.MagicMock(),
        }):
        from src.core.chat.utils import extract_and_renumber_citations
        from src.models.citation import Citation
        yield extract_and_renumber_citations, Citation

class TestExtractAndRenumberCitations:
    test_cases = {
        "complete_citation": {
            "chunk": "First citation [4].",
            "citation_map": {},
            "expected_chunk_to_yield": "First citation [1].",
            "expected_chunk_to_wait": "",
            "expected_citation_map": {"[4]": 1},
            "n_citations" : 4,
        },
        "complete_citation_with_existing_citations": {
            "chunk": "Second citation [4].",
            "citation_map": {"[2]" : 1},
            "expected_chunk_to_yield": "Second citation [2].",
            "expected_chunk_to_wait": "",
            "expected_citation_map": {"[2]" : 1, "[4]": 2},
            "n_citations" : 4,
        },
        "partial_citation": {
            "chunk": "First citation [4",
            "citation_map": {},
            "expected_chunk_to_yield": "First citation ",
            "expected_chunk_to_wait": "[4",
            "expected_citation_map": {},
            "n_citations" : 4,
        },
        "multiple_citations": {
            "chunk": "First citation [4]. Second citation [2].",
            "citation_map": {},
            "expected_chunk_to_yield": "First citation [1]. Second citation [2].",
            "expected_chunk_to_wait": "",
            "expected_citation_map": {"[4]": 1, "[2]": 2},
            "n_citations" : 4,
        },
        "multiple_citations_with_existing_citations": {
            "chunk": "First citation [4]. Repeat citation [7]. Third citation [2].",
            "citation_map": {"[7]" : 1},
            "expected_chunk_to_yield": "First citation [2]. Repeat citation [1]. Third citation [3].",
            "expected_chunk_to_wait": "",
            "expected_citation_map": {"[7]" : 1, "[4]": 2, "[2]": 3},
            "n_citations" : 7,
        },
        "partial_and_complete_citation": {
            "chunk": "First citation [4]. Second citation [2",
            "citation_map": {},
            "expected_chunk_to_yield": "First citation [1]. Second citation ",
            "expected_chunk_to_wait": "[2",
            "expected_citation_map": {"[4]": 1},
            "n_citations" : 4,
        },
        "no_citation": {
            "chunk": "This is not a citation [1a].",
            "citation_map": {},
            "expected_chunk_to_yield": "This is not a citation [1a].",
            "expected_chunk_to_wait": "",
            "expected_citation_map": {},
            "n_citations" : 1,
        },
        "complex_case": {
            "chunk": "[1][a][",
            "citation_map": {},
            "expected_chunk_to_yield": "[1][a]",
            "expected_chunk_to_wait": "[",
            "expected_citation_map": {"[1]": 1},
            "n_citations" : 1,
        },
        "catch_index_error_1" : {
            "chunk": "[9999]",
            "citation_map": {},
            "expected_chunk_to_yield": "[9999]", # It will yield the "[9999]" text but not the corresponding citation (which is not in the citation_map)
            "expected_chunk_to_wait": "",
            "expected_citation_map": {},
            "n_citations" : 9000, # Citation 9999 is in the chunk, but only 9000 available
        },
        "catch_index_error_2" : {
            "chunk": "[1][2][3]",
            "citation_map": {},
            "expected_chunk_to_yield": "[1][2][3]", # It will yield the "[3]" text but not the corresponding citation (which is not in the citation_map)
            "expected_chunk_to_wait": "",
            "expected_citation_map": {"[1]": 1, "[2]" : 2},
            "n_citations" : 2, # Citation 3 is in the chunk, but only 2 available
        }
    }
    
    @pytest.mark.parametrize("case_name, case_data", test_cases.items())
    def test_handle_citations_in_chunk(self,mock_inits_and_import_converters, case_name, case_data):
        extract_and_renumber_citations, Citation = mock_inits_and_import_converters #NOSONAR
        chunk = case_data["chunk"]
        citation_map = case_data["citation_map"]
        expected_chunk_to_yield = case_data["expected_chunk_to_yield"]
        expected_chunk_to_wait = case_data["expected_chunk_to_wait"]
        expected_citation_map = case_data["expected_citation_map"]
        n_citations = case_data["n_citations"]

        # Create fake Citations
        all_citations = []
        for i in range(n_citations):
            single_citation = Citation(
                content = f"fake_content_{i}",
                origin = "fake_origin",
                display_number = 12345, # This field is not used by the function
            )
            all_citations.append(single_citation)

        chunk_to_yield, chunk_to_wait, _ = extract_and_renumber_citations(chunk, citation_map, all_citations)

        assert chunk_to_yield == expected_chunk_to_yield
        assert chunk_to_wait == expected_chunk_to_wait
        assert citation_map == expected_citation_map
