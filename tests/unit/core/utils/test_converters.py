import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "src"))
import pytest
from enum import StrEnum
from unittest.mock import patch
from src.models import Citation, CitationType, CitationTag

@pytest.fixture
def mock_inits_and_import_converters(mocker):
    with patch.dict('sys.modules', {
        'src.core.bots.lambot': mocker.MagicMock(),
        'src.core.tools.registry': mocker.MagicMock(),
        "src.core.retrievers": mocker.MagicMock(),
        "src.core.retrievers.multi_retriever": mocker.MagicMock(),
        "src.core.retrievers.retriever": mocker.MagicMock(),
        "src.services.lifespan_service": mocker.MagicMock(),
        "src.core.utils.trace_sanitizer": mocker.MagicMock(),
        "src.core.base._base": mocker.MagicMock(),
        "src.core.base._app_utils": mocker.MagicMock(),
        "src.core.base._tool": mocker.MagicMock(),
        "src.core.base._graph": mocker.MagicMock(),
    }):
        from src.core.base._document import LamBotDocument
        import src.core.utils.converters as converters
        yield converters, LamBotDocument

class SampleExtensions(StrEnum):
    PDF = ".pdf"
    PPTX = ".pptx"
    XLSX = ".xlsx"
    DOCX = ".docx"

class TestGetFileExtension:

    def test_get_file_extension(self, mock_inits_and_import_converters):
        converters, _ = mock_inits_and_import_converters
        converters.FileExtension = SampleExtensions
        assert converters.get_file_extension("document.sample.pdf") == ".pdf"
        assert converters.get_file_extension("presentation.pptx") == ".pptx"
        assert converters.get_file_extension("spreadsheet.xlsx") == ".xlsx"
        assert converters.get_file_extension("document.docx") == ".docx"
        assert converters.get_file_extension("archive.zip") == None
        assert converters.get_file_extension("archive.tar.gz") == None
        assert converters.get_file_extension("no_extension") is None
        assert converters.get_file_extension("") is None

class TestConvertLambotDocumentsToCitations:


    def test_convert_lambot_single_document_to_citation(self, mock_inits_and_import_converters):
        converters, LamBotDocument = mock_inits_and_import_converters #NOSONAR
        lambot_document = LamBotDocument(
            llm_context="Sample context",
            origin="test_tool",
            page_content="Sample content",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample.pdf",
                "parent_url": "sample_url_for_sample.pdf",
                "author": "John Doe",
                "date": "2023-10-01"
            }

        )

        citation = converters.convert_lambot_documents_to_citations(
            [lambot_document],
            include_metadata=True
        )
        assert len(citation) == 1

    def test_convert_lambot_multiple_documents_to_citation(self, mock_inits_and_import_converters):
        converters, LamBotDocument = mock_inits_and_import_converters #NOSONAR
        lambot_document1 = LamBotDocument(
            llm_context="Sample context 1",
            origin="test_tool",
            page_content="Sample content 1",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample1.pdf",
                "parent_url": "sample_url_for_sample1.pdf",
                "author": "John Doe",
                "date": "2023-10-01"
            }
        )
        lambot_document2 = LamBotDocument(
            llm_context="Sample context 2",
            origin="test_tool",
            page_content="Sample content 2",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample2.pdf",
                "parent_url": "sample_url_for_sample2.pdf",
                "author": "Jane Doe",
                "date": "2023-10-02"
            }
        )
        citation = converters.convert_lambot_documents_to_citations(
            [lambot_document1, lambot_document2],
            include_metadata=True
        )
        assert len(citation) == 2

    
    def test_convert_lambot_list_of_documents_to_citation(self, mock_inits_and_import_converters):
        converters, LamBotDocument = mock_inits_and_import_converters #NOSONAR
        lambot_document1 = LamBotDocument(
            llm_context="Sample context 1",
            origin="test_tool",
            page_content="Sample content 1",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample1.pdf",
                "parent_url": "sample_url_for_sample1.pdf",
                "author": "John Doe",
                "date": "2023-10-01"
            }
        )
        lambot_document2 = LamBotDocument(
            llm_context="Sample context 2",
            origin="test_tool",
            page_content="Sample content 2",
            citation_field_mappings={},
            metadata={
                "parent_filename": "sample2.pdf",
                "parent_url": "sample_url_for_sample2.pdf",
                "author": "Jane Doe",
                "date": "2023-10-02"
            }
        )
        citation = converters.convert_lambot_documents_to_citations(
            [[lambot_document1, lambot_document2]],
            include_metadata=True
        )
        assert len(citation) == 1

    