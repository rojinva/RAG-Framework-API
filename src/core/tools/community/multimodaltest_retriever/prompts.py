"""
Disclaimer: Please note that these fallback prompts are not regularly updated. 
"""

MULTIMODAL_INSTRUCTION_PROMPT = """
**Interpreting Table Data:**
- Accurately interpret semiconductor industry-specific metrics (nm, GHz, wafers/month, yield percentages).
- Align numerical data precisely with row and column headers.
- If a table is partially cropped or unclear, do not guess the number and the information might not be formatted well in the source document.

Base your answers solely on the sources provided below. Always include in-text citations formatted as numbers in square brackets (e.g., [1]) when referencing information from these sources. If citing multiple sources, list each citation separately (e.g., [1][2]).

Sources:
"""

MULTIMODAL_TOOL_DESCRIPTION_PROMPT = """
Useful for providing concise, source-based answers to Lam Research employees' questions about semiconductor equipment questions.
"""