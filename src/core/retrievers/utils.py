import re
from src.core.base import LamBotDocument
from typing import List, Union
from collections import defaultdict
from src.core.retrievers.pii_data import customer_names_case_insensitive, customer_names_case_sensitive


def group_lambot_documents(
    lambot_documents: List[LamBotDocument],
) -> List[Union[LamBotDocument, List[LamBotDocument]]]:
    """Group LamBot Documents based on the same "parent_filename" field and
    additional citation fields defined in citation_field_mappings.
    If a group has only one document, that document is returned individually.
    For groups with more than one document, all the documents are returned within a list.

    Args:
        lambot_documents: (List[LamBotDocument]): List of lambot documents to group.

    Returns:
        List[Union[LamBotDocument, List[LamBotDocument]]]: List where individual lambot documents that were not grouped
                                                           remain as standalone lambot documents and groups with multiple lambot documents
                                                           are returned as lists.
    """
    # Group documents by parent_filename and citation fields
    grouped_documents = defaultdict(list)
    for document in lambot_documents:
        key = document.metadata.get("parent_filename", "")
        citation_field_mappings = document.citation_field_mappings
        for citation_field in citation_field_mappings.keys():
            key += str(document.metadata.get(citation_field, ""))
        grouped_documents[key].append(document)

    # Return grouped documents
    result = []
    for key, documents in grouped_documents.items():
        if len(documents) == 1:
            result.append(documents[0])
        else:
            result.append(documents)
    return result

def create_llm_context_string(grouped_documents: List[Union[LamBotDocument, List[LamBotDocument]]]) -> str:
    """Create a string representation of the llm_context for each grouped document.

    Args:
        grouped_documents: (List[Union[LamBotDocument, List[LamBotDocument]]]): List of grouped documents.

    Returns:
        str: A string representation of the llm_context for each grouped document.
    """
    concatenated_llm_context = ""
    for index, item in enumerate(grouped_documents, start=1):
        if isinstance(item, list):
            llm_contexts = "\n...\n".join(str(doc.llm_context) for doc in item)
        else:
            llm_contexts = str(item.llm_context)
        
        concatenated_llm_context += f"[{index}] {llm_contexts}\n\n"

    return concatenated_llm_context.strip()

def construct_pattern(pii_list: List[str], case_insensitive: bool = False) -> re.Pattern:
    """
    Constructs a regex pattern for redacting PII.

    Parameters:
    pii_list (list): A list of words (PII) to be redacted from the text.
    case_insensitive (bool): Flag to indicate if the pattern should be case-insensitive.

    Returns:
    re.Pattern: The compiled regex pattern.
    """
    pattern = r"(?<![A-Za-z])(" + "|".join([re.escape(word).replace(r"\ ", r"[\s_-]+") for word in pii_list]) + r")(?![A-Za-z])"
    if case_insensitive:
        return re.compile(pattern, re.IGNORECASE)
    else:
        return re.compile(pattern)

def redact_pii(text: str, pii_list_case_insensitive: List[str] = customer_names_case_insensitive, pii_list_case_sensitive: List[str] = customer_names_case_sensitive, redaction_string: str = "<CUSTOMER>") -> str:
    """
    Redacts words in the pii_list_case_insensitive and pii_list_case_sensitive from the given text by replacing them with the redaction_string.

    Parameters:
    text (str): The input string containing the text to be redacted.
    pii_list_case_insensitive (list): A list of words (PII) to be redacted from the text in a case-insensitive manner.
    pii_list_case_sensitive (list): A list of words (PII) to be redacted from the text in a case-sensitive manner.
    redaction_string (str): The string to replace the PII with. Default is "<CUSTOMER>".

    Returns:
    str: The redacted text with PII replaced by the redaction_string.

    Note:
    The redaction for pii_list_case_insensitive is case-insensitive and handles variations with spaces, underscores, hyphens, and multiple spaces.
    The redaction for pii_list_case_sensitive is case-sensitive and handles variations with spaces, underscores, hyphens, and multiple spaces.
    It also covers edge cases where numbers or special characters are part of the PII.
    """

    # Compile pattern for case-insensitive redaction
    pattern_case_insensitive = construct_pattern(pii_list_case_insensitive, case_insensitive=True)

    # Compile pattern for case-sensitive redaction
    pattern_case_sensitive = construct_pattern(pii_list_case_sensitive)

    # Replace matched words with the redaction_string
    redacted_text = pattern_case_insensitive.sub(redaction_string, text)
    redacted_text = pattern_case_sensitive.sub(redaction_string, redacted_text)

    return redacted_text

