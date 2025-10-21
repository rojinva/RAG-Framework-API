"""SharePoint response formatting utilities."""

from typing import Dict, Any, List

from pydantic import AnyUrl
import logging

logger = logging.getLogger(__name__)


def format_sharepoint_results(api_response: Dict[str, Any]) -> str:
    """
    Format SharePoint API response into a readable string with markdown URLs.

    Args:
        api_response: The response from Microsoft Graph Copilot API

    Returns:
        Formatted results string
    """
    try:
        # Extract results from the response using the correct schema
        retrieval_hits = api_response.get("retrievalHits", [])

        if not retrieval_hits:
            return "No results found in SharePoint for the given query."

        formatted_results = []

        for i, hit in enumerate(retrieval_hits, 1):
            # Extract metadata with fallbacks
            resource_metadata = hit.get("resourceMetadata", {})
            title = resource_metadata.get("title", f"SharePoint Document {i}")
            author = resource_metadata.get("author", "Unknown Author")
            url = hit.get("webUrl", "#")  # Use "#" as default for missing URLs

            # Extract and combine all text extracts
            extracts = hit.get("extracts", [])
            extract_texts = []
            for extract in extracts:
                text = extract.get("text", "")
                if text:
                    extract_texts.append(text)

            combined_content = (
                " ".join(extract_texts)
                if extract_texts
                else "No content available"
            )

            # Format each result
            result_text = f"""[{title}]({url})
**Author**: {author}
**Extract**: {combined_content}"""
            formatted_results.append(result_text)

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"An error occurred while formatting the results: {str(e)}"


def format_sharepoint_filter_expression(sharepoint_urls: List[AnyUrl]) -> str:
    """
    Given a list of SharePoint URLs, create a filter expression string.
    Example: path:"https://contoso.sharepoint.com/sites/HR1/" OR path:"https://contoso.sharepoint.com/sites/HR2/"
    """
    # Create individual path filters for each URL
    path_filters = [f'path:"{url}"' for url in sharepoint_urls]
    # Combine all path filters with OR
    combined_filter = " OR ".join(path_filters)
    return combined_filter