from copy import copy
from src.models import Citation, CitationType, CitationTag
from src.models.constants import FileExtension
from src.core.base._document import LamBotDocument
from typing import List, Union, Optional

def get_file_extension(parent_path: str) -> Optional[FileExtension]:
    """
    Determine the file extension based on the file extension extracted from the 'parent_path' in the metadata.

    This function extracts the file extension from the parent path, and matches it against 
    the FileExtension enum members.
    It returns the corresponding FileExtension if a match is found, otherwise None.

    Parameters:
    parent_path (str): The parent path of the file from which the file extension is extracted.

    Returns:
    Optional[FileExtension]: The FileExtension enum member corresponding to the file's
                        extension, or None if no match is found.
    """

    # Extract the file extension from the parent_path
    file_extension = f".{parent_path.split('.')[-1].lower()}"
    # Check against each FileExtension enum member
    for file_extension_enum in FileExtension:
        if file_extension == file_extension_enum.value:
            return file_extension_enum
    return None


def convert_lambot_documents_to_citations(
    documents: List[Union[LamBotDocument, List[LamBotDocument]]], 
    include_metadata: bool = False
) -> List[Citation]:
    """
    Convert a list of lambot documents into a list of Citation objects.
    Note: Langfuse DOES NOT receive Citation objects. Instead, it receives data upstream from the retriever in the form of LamBotDocuments.

    Parameters:
    documents (List[Union[LamBotDocument, List[LamBotDocument]]]): 
        A list of lambot documents to be converted into Citation objects.
    include_metadata (bool): If True, includes metadata processing, extracting fields such as filename, URL, and tags,
                             and excluding 'chunk_vector'.
                             If False, only the content and display number are included.

    Returns:
    (List[Citation]): A list of Citation objects.
    """

    citations = []
    for display_number, document in enumerate(documents, start=1):

        if isinstance(document, list) and all(isinstance(doc, LamBotDocument) for doc in document):
            lambot_document = document[0]  # Use the first document for metadata for grouped LamBotDocument
        elif isinstance(document, LamBotDocument):
            lambot_document = document
        else:
            raise ValueError("Document must be of type Document or LamBotDocument")
        
        # Tool that generated the citation
        origin = lambot_document.origin
        citation_field_mappings = lambot_document.citation_field_mappings

        # Create the base Citation object without the content field
        citation = Citation(
            display_number=display_number,
            origin=origin
        )

        if include_metadata:
            # Initialize metadata as an empty dictionary if it doesn't exist
            metadata = copy(getattr(lambot_document, "metadata", {}))

            # Extract filename and URL from metadata if they exist
            filename = metadata.pop("parent_filename", None)
            url = metadata.pop("parent_url", None)

            parent_path = metadata.get("parent_path", None)
            file_extension = get_file_extension(parent_path) if parent_path else None

            # Extract filename and URL for citation fields, then remove from metadata
            citation_type = (
                CitationType.pdf_unstructured
                if filename and filename.lower().endswith(".pdf")
                else CitationType.unstructured
            )

            # Update the Citation object with optional fields
            citation.type = citation_type
            citation.display_name = filename
            citation.url = url

            # Values to skip
            skip_values = [-1, ""]

            # Create CitationTag objects based on the citation_mapping
            citation.tags = []
            for key, value in metadata.items():
                if value not in skip_values and key in citation_field_mappings:
                    citation_tag_alias_spec = citation_field_mappings[key]
                    citation.tags.append(
                        CitationTag(
                            display_name=citation_tag_alias_spec.file_extension_aliases.get(file_extension, citation_tag_alias_spec.default) if citation_tag_alias_spec.file_extension_aliases else citation_tag_alias_spec.default,
                            content=str(value),
                            is_visible=True
                        )
                    )

        citations.append(citation)

    return citations