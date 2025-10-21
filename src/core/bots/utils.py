import re
from src.models import MultiRetrieverToolSpec

def uppercase_smash_case(prefix):
    """
    Normalize a given prefix string by removing symbols and extra spaces,
    then converting it to uppercase and removing spaces to create a smash case string.

    Args:
        prefix (str): The input prefix string to be normalized.

    Returns:
        str: The normalized smash case string.
    """
    # Example string: "Quest+ (POC 3 4) Q "
    
    # Step 1: Remove symbols, keep only letters, numbers, and spaces
    # Result: "Quest POC 3 4 Q "
    prefix_without_symbols = re.sub(r'[^a-zA-Z0-9\s]', '', prefix)
    
    # Step 2: Replace multiple spaces with a single space
    # Result: "Quest POC 3 4 Q "
    prefix_single_spaced = re.sub(r'\s+', ' ', prefix_without_symbols)
    
    # Step 3: Convert to uppercase and remove spaces to create smash case
    # Result: "QUESTPOC34Q"
    smash_case_prefix = prefix_single_spaced.upper().replace(" ", "")
    
    return smash_case_prefix

def create_multiretriever_tool_spec(prefix):
    """
    Create a MultiRetrieverToolSpec object using a normalized prefix to generate
    prompt names for instruction and tool description.

    Args:
        prefix (str): The input prefix string to be normalized and used for generating prompt names.

    Returns:
        MultiRetrieverToolSpec: The created MultiRetrieverToolSpec object with the generated prompt names.
    """

    normalized_prefix = uppercase_smash_case(prefix)
    instruction_prompt_name = f"{normalized_prefix}_INSTRUCTION_PROMPT"
    tool_description_prompt_name = f"{normalized_prefix}_TOOL_DESCRIPTION_PROMPT"

    global_vars = globals()

    return MultiRetrieverToolSpec(
        tool_name="multi_retriever",
        prompts={
            "instruction_prompt": (
                instruction_prompt_name,
                global_vars.get(instruction_prompt_name, None),
            ),
            "tool_description_prompt": (
                tool_description_prompt_name,
                global_vars.get(tool_description_prompt_name, None),
            ),
        },
    )