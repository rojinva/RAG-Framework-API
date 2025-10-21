import re
from typing import List, Dict, Tuple, Optional

from src.models.citation import Citation
from src.core.tools.common import LamBotMultiRetrieverTool, LamBotRetrieverTool
from src.core.bots import LamBot


def extract_and_renumber_citations(chunk: str,
                                   citation_map: Dict[str, int],
                                   all_citations: Optional[List[Citation]],
                                   ) -> Tuple[str, str]:
    """
    Processes a to-be-streamed chunk of text to find and renumber any citations, updating the citation map with new citations and replacing original citation numbers with renumbered values.

    Args:
        chunk (str): The chunk of text to process for citations.
        citation_map (Dict[str, int]): A dictionary mapping original citation strings to their mapped values.
        all_citations (Optional[List[Citation]]): List of original Citation objects. If None, there are no citations.

    Returns:
        chunk_to_yield (str): The processed chunk of text, which will be yielded in a LamBotChatResponse.
        chunk_to_wait (str): Any remaining partial citation suffix. The next streaming chunk will append to this.
        citations_to_yield (List[Citation]): List of found, not-yet-yield Citations, which will be yielded in a LamBotChatResponse.
    """

    if not all_citations:
        return chunk, "", []

    COMPLETE_CITATION_REGEX = r'\[\d+\]'
    TEMPORARY_PLACEHOLDER_REGEX = r'\[<(\d+)>]'
    PARTIAL_CITATION_SUFFIX_REGEX = r'\[\d*$'

    # Check for complete citations, e.g. "end. [4][2]. Beg"
    citations_to_yield = []
    matches = re.findall(COMPLETE_CITATION_REGEX, chunk)
    if matches:
        for match in matches:
            # Check if it's a newly used citation
            if match not in citation_map:
                # If so, update the citation map, get the Citation, and renumber it
                old_citation_index = int(match[1:-1]) - 1 # Old index of the Citation in all_citations
                try:
                    citation = all_citations[old_citation_index]
                except IndexError:
                    print(f"LLM cited {match} but there are only {len(all_citations)} citations.")
                    continue
                new_citation_index = len(citation_map) # New index of the Citation
                citation_map[match] = new_citation_index + 1
                citation.is_used = True # Mark the citation as used
                citations_to_yield.append(citation)

            # Replace original citation number with citation map value
            # To avoid accidentally replacing multiple times, temprarily use a placeholder with extra <>, e.g. "[<1>]"
            chunk = chunk.replace(match, f'[<{citation_map[match]}>]')

        # Replace all temporary placeholders
        chunk = re.sub(TEMPORARY_PLACEHOLDER_REGEX, r'[\1]', chunk)

    # Check if chunk ends with a possible citation, e.g. "end. [1"
    match = re.search(PARTIAL_CITATION_SUFFIX_REGEX, chunk)
    if match:
        # If so, yield the prefix and wait on the suffix
        chunk_to_yield = chunk[:match.start()]
        chunk_to_wait = match.group()
    else:
        # If not, yield the whole chunk and don't wait on anything
        chunk_to_yield = chunk
        chunk_to_wait = ""

    return chunk_to_yield, chunk_to_wait, citations_to_yield


def extract_indexes_queried_by_agent(bot: LamBot) -> List[str]:
    """
    This function takes a bot instance and returns a list of indexes queried by the tools by the Agent.
    
    Args:
    bot (LamBot): The bot instance containing configured tools.

    Returns:
    list: A list of index names queried by the tools within the bot.
    """
    
    indexes_used = []
    for tool in bot._tools:
        if isinstance(tool, LamBotMultiRetrieverTool):
            retriever_tools = tool.retriever_tools
            for retriever_tool in retriever_tools:
                indexes_used.append(retriever_tool.tool_spec.index_name)
        elif isinstance(tool, LamBotRetrieverTool):
            indexes_used.append(tool.tool_spec.index_name)
    return indexes_used
    
    
    

