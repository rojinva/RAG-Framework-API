# Community Directory

The `community` directory is designed to house tools and configurations related to various use cases. This directory includes fallback prompts, tool configurations, and tools that are essential for the use cases.

## Quick Start Guide

1. **Include Fallback Prompts:**
   - Ensure your tools have fallback prompts in `prompts.py`.
   - Always provide fallback prompts in the `prompts.py` files. These are essential for ensuring the tools can function even if Langfuse is unavailable.
   - Ensure that the descriptions are clear and describe exactly what the tool should be used for. The tool description prompt is very important and is used by the agent to determine which tool to call based on the user question.

2. **Define Tool Spec:**
   - Create clear and comprehensive tool configurations directly in the `tool.py` files. For retriever tools, these configurations should include details such as the tool name, index name, prompt names, search configurations, and tool type. Use the `RetrieverToolSpec` or `MultiRetrieverToolSpec` class for defining these specifications.

3. **Register Tools:**
   - Register the tools using the `register_tool` helper function in the `__init__.py` file of the folder to make them available in the LamBot API.

## Directory Structure

The `community` directory is structured as follows:

    community/
    ├── init.py
    ├── tool_1/
    │   ├── init.py
    │   ├── prompts.py
    │   ├── retriever_tool.py
    │   └── ...
    ├── tool_2/
    │   ├── init.py
    │   ├── prompts.py
    │   ├── multi_retriever_tool.py
    │   └── ...
    └── ...

## Fallback Prompts

Fallback prompts are default prompts used by the tools when specific prompts are not available from Langfuse. These prompts are stored locally and are used as a backup to ensure the tools can still function even if LangFuse is unavailable.

### Example of Defining Fallback Prompts

In the `prompts.py` file, you can define fallback prompts like this:

```python
EXAMPLE_INSTRUCTION_PROMPT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
EXAMPLE_TOOL_DESCRIPTION_PROMPT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
```

## ToolSpec
The `RetrieverToolSpec` and `MultiRetrieverToolSpec` data classes are used to define the specifications for tools. Here are their attributes:

| Attribute                | Description                                                                 | RetrieverToolSpec | MultiRetrieverToolSpec |
|--------------------------|-----------------------------------------------------------------------------|-------------------|------------------------|
| **tool_name**            | Name of the tool. This will be used for reference in the LamBot config.   | ✔                 | ✔                      |
| **prompts**              | A dictionary of prompts for the tool.                                       | ✔                 | ✔                      |
| **index_name**           | Name of the index in Azure Search Service                                                          | ✔                 |                        |
| **search_config**        | A dictionary containing the Azure Search configuration for the tool.              | ✔                 |                        |
| **citation_field_mappings** (Optional) | A dictionary for citation field mappings. This is opt-in. By default, the app will only display `parent_filename` hyperlinked to `parent_url` on the app. For example, `{"row": "Page"}` means the field `row` from the search index will be displayed as `Page` on the frontend. | ✔                 |                        |
| **access_control** (Optional) | Configuration for access control.                                      | ✔                 |                        |
| **formatter** (Optional) | An optional formatter for the tool. This allows configuring a tool response to be in a custom markdown-supported format.                                          | ✔                 |                        |   


### AccessControl

The AccessControl data class is used to define access control configurations, which is particularly useful for something like a CCI retriever. However, it has been added to LamBots as a foundational capability. A function, param, and filter field are all you need to enable granular access to chunks in the index:

- **function**: A function that the developer writes, which accepts either a username or email (as a string) and returns a list. This list contains the access types for the user. If the user doesn't have access to the specified chunks in the index, the function returns an empty list.
- **param**: The parameter type for the access control function, which can be either USERNAME or EMAIL.
- **filter_field**: The field in the search service to be filtered. The list returned by the function is used to curate a filter query. If the list is empty, the search results will return an empty response.

This process ensures tools are properly configured and registered, making them available for use in the LamBot API.

## Example Tool Creation
An example tool creation might look like this:

```python
from src.models import ToolType, RetrieverToolSpec, AccessControl, AccessControlParam
from .prompts import (
    EXAMPLE_INSTRUCTION_PROMPT,
    EXAMPLE_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from ..utils import get_example_access_types

tool_spec = RetrieverToolSpec(
    tool_name="example_retriever",
    index_name="index-example",
    prompts={
        "instruction_prompt": (
            "EXAMPLE_INSTRUCTION_PROMPT",
            EXAMPLE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EXAMPLE_TOOL_DESCRIPTION_PROMPT",
            EXAMPLE_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "queryType": "semantic",
        "semanticConfiguration": "example-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    access_control=AccessControl(
        function=get_example_access_types,  # The function to get access types
        param=AccessControlParam.EMAIL,  # The parameter type for the access control function
        filter_field="sheet_name",  # The field in the search service to be filtered
    ),
    citation_field_mappings={
        "row": CitationTagAliasSpec(
            default="ROW",
            file_extension_aliases={
                FileExtension.XLS: "Row",
                FileExtension.XLSX: "Row",
                FileExtension.PPT: "Slide",
                FileExtension.PPTX: "Slide",
                FileExtension.PDF: "Page",
                FileExtension.DOC: "Page",
                FileExtension.DOCX: "Page",
            },
        ),
        "sheet_name": CitationTagAliasSpec(
            default="SHEET NAME",
            file_extension_aliases={
                FileExtension.XLS: "Sheet name",
                FileExtension.XLSX: "Sheet name",
                FileExtension.DOC: "Section name",
                FileExtension.DOCX: "Section name",
            },
        ),
    },
)

example_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
```
#### Note: Specifying a value for `k` in `vectorQueries` will override the `k` value set in the `QueryConfig` or by the user in the app. If `k` value is not provided for the `vectorQueries`, the tool will not send a `k` value at all, resulting in `k=null` or `k=50`.

#### What *citation_field_mappings* Does:
The `citation_field_mappings` is a configuration dictionary that defines how fields in the search index are displayed in citations. Each entry in the dictionary corresponds to a field in the index and is associated with a `CitationTagAliasSpec` object. This object specifies both a default alias and file-type-specific aliases, allowing for flexible and contextually appropriate citation displays.

##### How It Works
**Default Alias**: Each field has a default alias that is used when no specific file type alias is applicable. For example, the default alias for the row field in the citation field mapping above is "ROW".

**File-Type Specific Aliases**: The `file_extension_aliases` dictionary within each `CitationTagAliasSpec` provides specific aliases for different file types, as defined by the `FileExtension` enum. This allows the citation display to adapt based on the document type:

- Row Field:
    - Excel Files (.xls, .xlsx): Displayed as "Row".
    - PowerPoint Files (.ppt, .pptx): Displayed as "Slide".
    - PDF and Word Files (.pdf, .doc, .docx): Displayed as "Page".
- Sheet Name Field:
    - Excel Files (.xls, .xlsx): Displayed as "Sheet name".
    - Word Files (.doc, .docx): Displayed as "Section name".

## Example MultiRetrieverTool Creation
An example multi-retriever tool creation might look like this:
```python
from src.core.tools.common.retriever import LamBotMultiRetrieverTool
from src.core.tools.community.example_retriever_1 import example_retriever_tool_1
from src.core.tools.community.example_retriever_2 import example_retriever_tool_2
from src.models.retriever_tool import MultiRetrieverToolSpec
from src.core.tools.common.prompts import MULTIRETRIEVER_INSTRUCTION_PROMPT as EXAMPLE_MULTIRETRIEVER_INSTRUCTION_PROMPT
from src.core.tools.common.prompts import MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT as EXAMPLE_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT

tool_spec = MultiRetrieverToolSpec(
    tool_name="example_multi_retriever",
    prompts={
        "instruction_prompt": (
            "EXAMPLE_MULTIRETRIEVER_INSTRUCTION_PROMPT",
            EXAMPLE_MULTIRETRIEVER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EXAMPLE_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT",
            EXAMPLE_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

example_multi_retriever_tool = LamBotMultiRetrieverTool.from_tools(
    retriever_tools=[example_retriever_tool_1, example_retriever_tool_2],
    tool_spec=tool_spec,
)
```

## Registering the Tool
Register the tool in `__init__.py` to make it available in the LamBot API:
```python
from .retriever_tool import example_retriever_tool
from .multi_retriever_tool import example_multi_retriever_tool
from src.core.tools.registry import register_tool

register_tool(example_retriever_tool)
register_tool(example_multi_retriever_tool)
```

This process ensures tools are properly configured and registered, making them available for use in the LamBot API.

## MultiRetriever Prompt Selection
#### <span style="color:red">Disclaimer: This section explains the process of selecting the multiretriever prompt for a LamBot that has more than one retriever tools and when the combine retriever tools flag is set to true. This process is dynamic and based on the LamBot display name.</span>

### Example Flow

#### Step 1: Normalize the Prefix
The prefix is normalized to uppercase smash case, removing symbols, brackets, spaces, and any special characters.

- **Input**: `Insight Management`
    - **Normalized Prefix**: `INSIGHTMANAGEMENT`
- **Input**: `Quest+`
    - **Normalized Prefix**: `QUEST`
- **Input**: `Design Insights 2`
    - **Normalized Prefix**: ` DESIGNINSIGHTS2`

#### Step 2: Generate Prompt Names
Using the normalized prefix, generate the prompt names for instruction and tool description.

- For "Insight Management":
    - **Instruction Prompt Name**: `INSIGHTMANAGEMENT_INSTRUCTION_PROMPT`
    - **Tool Description Prompt Name**: `INSIGHTMANAGEMENT_TOOL_DESCRIPTION_PROMPT`

- For "Quest+":
    - **Instruction Prompt Name**: `QUEST_INSTRUCTION_PROMPT`
    - **Tool Description Prompt Name**: `QUEST_TOOL_DESCRIPTION_PROMPT`

#### Step 3: Fetch Prompts with Fallback Logic
When the combine retriever tools flag is set to true, the system fetches the primary prompt specified by the prompt key. If the primary prompt is not available, it falls back to a secondary prompt. The fallback logic works as follows:

1. Attempt to retrieve the primary prompt using *primary_prompt_name* (e.g., `INSIGHTMANAGEMENT_INSTRUCTION_PROMPT`).
2. If the primary prompt is not available on Langfuse, use local *primary_fallback_prompt* (e.g., `INSIGHTMANAGEMENT_INSTRUCTION_PROMPT`).
3. If *primary_fallback_prompt* is not available, attempt to retrieve the secondary fallback prompt from Langfuse using *secondary_fallback_prompt_name* (`MULTIRETRIEVER_INSTRUCTION_PROMPT`).
4. If the secondary fallback prompt is not available on Langfuse, use *secondary_fallback_prompt* stored locally (`MULTIRETRIEVER_INSTRUCTION_PROMPT`).