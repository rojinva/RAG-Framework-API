"""
Disclaimer: Please note that these fallback prompts are not regularly updated. 
"""

REDACTED_ETCH_INSTRUCTION_PROMPT = """
**Handling Redacted Information:**
- This data source contains redacted numerical values for confidentiality purposes.
- Redacted numbers appear in the format <NUMBER>.
- Do NOT attempt to guess, estimate, or infer any values that appear as <NUMBER>.
- Focus your analysis on non-redacted information only and acknowledge when specific numerical data is unavailable due to redaction.

Base your answers solely on the sources provided below. Always include in-text citations formatted as numbers in square brackets (e.g., [1]) when referencing information from these sources. If citing multiple sources, list each citation separately (e.g., [1][2]).

Sources:
"""

REDACTED_ETCH_TOOL_DESCRIPTION_PROMPT = """
Useful for providing concise, source-based answers to Lam Research employees' questions about semiconductor etch equipment questions.
"""