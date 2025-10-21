"""
Disclaimer: Please note that these fallback prompts are not regularly updated. 
"""

TEXT_TO_SQL_INSTRUCTION_PROMPT = """
Based on the response from the sql query, answer the question provided. Remedies if any are provided.
"""

TEXT_TO_SQL_QUERY_GENERATION_PROMPT = """
Using the information provided, generate a SQL query that can be used to extract the required information from the database. Follow the rules and guidelines below to ensure the query is accurate and adheres to the given constraints.
Only generate queries based on the metadata, schema, and sample queries provided as part of the information. Do not make assumptions or use external knowledge.
Generate a query that only comes from the information provided. If the information is not related at all, generate "SELECT COLUMN FROM TABLE".
Never use SELECT *. Always specify the fields to use in the query.
When limiting the number of results, use SELECT TOP instead of LIMIT in the query.
Ensure that the fields and tables used in the query match the provided schema and metadata.
Follow standard SQL query structure and syntax to ensure the query is valid and executable.
If there is no context provided in the SCHEMA for the question asked, use the sample queries to generate the query.
"""

TEXT_TO_SQL_TOOL_DESCRIPTION_PROMPT = """
Useful for providing concise, source-based answers coming from a SQL database to Lam Research employees' questions. Ensure calling the tool with an appropriate SQL Query and try not to use generic information to answer the question.
"""