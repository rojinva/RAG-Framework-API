import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "src"))
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_inits_and_import_converters(mocker):
    with patch.dict('sys.modules', {
        'src.core.bots.lambot': mocker.MagicMock(),
        'src.core.tools.registry': mocker.MagicMock(),
        'src.core.retrievers': mocker.MagicMock(),
        'src.core.retrievers.retriever': mocker.MagicMock(),
        'src.core.retrievers.MultiRetriever': mocker.MagicMock(),
        "src.core.base._base": mocker.MagicMock(),
        "src.core.base._app_utils": mocker.MagicMock(),
        "src.core.base._tool": mocker.MagicMock(),
        "src.core.base._graph": mocker.MagicMock(),
    }):
        from src.core.base._document import LamBotDocument
        from src.core.rerankers.semantic_reranker import SemanticReranker
        yield SemanticReranker(), LamBotDocument
    
class TestCompressDocument:

    def test_compress_document(self, mock_inits_and_import_converters):
        SemanticReranker, LamBotDocument = mock_inits_and_import_converters #NOSONAR
        lambot_document_1 = LamBotDocument(
            llm_context="Sample context",
            origin="test_tool",
            page_content="Sample content",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample.pdf",
                "parent_url": "sample_url_for_sample.pdf",
                "author": "John Doe",
                "date": "2023-10-01",
                "@search.rerankerScore": 0.8
            }
        )
        lambot_document_2 = LamBotDocument(
            llm_context="Sample context",
            origin="test_tool",
            page_content="Sample content",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample2.pdf",
                "parent_url": "sample_url_for_sample2.pdf",
                "author": "Jane Doe",
                "date": "2023-10-02",
                "@search.rerankerScore": 0.9
            }
        )
        result = SemanticReranker.compress_documents(
            [lambot_document_1, lambot_document_2]
        )
        assert result[0].metadata["@search.rerankerScore"] == pytest.approx(0.9)
        assert result[1].metadata["@search.rerankerScore"] == pytest.approx(0.8)

    
    def test_compress_document_no_reranker_score_metadata(self, mock_inits_and_import_converters):
        SemanticReranker, LamBotDocument = mock_inits_and_import_converters #NOSONAR
        lambot_document_1 = LamBotDocument(
            llm_context="Sample context",
            origin="test_tool",
            page_content="Sample content",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample.pdf",
                "parent_url": "sample_url_for_sample.pdf",
                "author": "John Doe",
                "date": "2023-10-01",
            }
        )
        lambot_document_2 = LamBotDocument(
            llm_context="Sample context",
            origin="test_tool",
            page_content="Sample content",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample2.pdf",
                "parent_url": "sample_url_for_sample2.pdf",
                "author": "Jane Doe",
                "date": "2023-10-02",
                "@search.rerankerScore": 0.9
            }
        )
        with pytest.raises(KeyError):
            SemanticReranker.compress_documents(
                [lambot_document_1, lambot_document_2]
            )