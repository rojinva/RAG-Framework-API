"""
Disclaimer: Please note that these fallback prompts are not regularly updated. 
"""

ACLMO_INSTRUCTION_PROMPT = """
**Instructions for Interpreting Images and Tables:**
- Carefully review all provided images, especially when multiple similar images or versions of data are present.
- Identify explicit indicators of recency (e.g., timestamps, dates, version numbers) and after comparing these indicators carefully choose the most recent or updated data.

**Interpreting Table Data:**
- Accurately interpret semiconductor industry-specific metrics (nm, GHz, wafers/month, yield percentages).
- Align numerical data precisely with row and column headers.
- If a table is partially cropped or unclear, do not guess the number and the information might not be formatted well in the source document.

Base your answers solely on the sources provided below. Always include in-text citations formatted as numbers in square brackets (e.g., [1]) when referencing information from these sources. If citing multiple sources, list each citation separately (e.g., [1][2]).

Sources:
"""

ACLMO_TOOL_DESCRIPTION_PROMPT = """
Useful for providing concise, source-based answers to Lam Research employees' questions about semiconductor etch equipment questions.
"""