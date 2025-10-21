"""
Prompts for the SharePoint Copilot API Tool.
"""

SHAREPOINT_TOOL_DESCRIPTION_PROMPT = """Search SharePoint documents and content using Microsoft Graph Copilot API. 
This tool searches across specific SharePoint sites, returning relevant content. 
Use this tool when users need to find information from SharePoint documents, 
policies, procedures, or any content stored in SharePoint."""

SHAREPOINT_INSTRUCTION_PROMPT = """Based on the SharePoint search results below, provide a comprehensive answer to the user's question. 
If the information is insufficient, say that you don't know the answer. Do not generate answers from sources not included in the list.  
Please ensure to include these in-text url citations in the final answer.
SharePoint Search Results:
"""
