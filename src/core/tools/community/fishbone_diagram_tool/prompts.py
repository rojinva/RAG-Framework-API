FISHBONE_DIAGRAM_TOOL_DESCRIPTION_PROMPT = """
This tool creates a visual Fishbone (Ishikawa) diagram to analyze root causes of a problem.

WHAT THIS TOOL DOES:
- Creates a structured visualization showing cause-and-effect relationships
- Organizes potential causes into categories
- Helps identify root causes of problems or issues

INPUT FORMAT:
Provide a dictionary where:
- Keys represent main categories (e.g., "People", "Process", "Technology"). Try to limit to max of 20 categories
- Values are lists of specific causes within each category (e.g., ["Lack of training", "Poor communication"] . Try to limit each cause to 50 characters and a max of 20 causes in each category)
"""
