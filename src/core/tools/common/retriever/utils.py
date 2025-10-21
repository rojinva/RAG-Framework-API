from typing import Any, Optional, Tuple, Union


def merge_search_filters(
    filter_clauses: list[str], operator: Optional[str] = "and"
) -> str:
    """
    Merge multiple search filter strings with the specified logical operator ("and"/"or").

    Args:
        filter_clauses (list[str]): List of search filter strings to merge.
        operator (Optional[str]): The logical operator to use ("and" or "or"). Defaults to "and".
    Returns:
        str: The merged search filter string.
    """
    op_lower = operator.lower()
    if op_lower not in ["and", "or"]:
        raise ValueError("Operator for merging search filters must be 'and' or 'or'.")

    # Filter out empty/None filters
    cleaned_filters = [f for f in filter_clauses if f]
    if not cleaned_filters:
        return ""
    if len(cleaned_filters) == 1:
        return cleaned_filters[0]

    def _wrap_parentheses(f: str) -> str:
        if f.startswith("(") and f.endswith(")"):
            return f
        f_lower = f.lower()
        if " and " in f_lower or " or " in f_lower:
            return f"({f})"
        return f

    wrapped_filters = [_wrap_parentheses(f) for f in cleaned_filters]
    return f" {op_lower} ".join(wrapped_filters)


def _group_by_type(
    items: list[Any],
) -> Tuple[list[str], list[Union[int, float]], list[bool]]:
    """Group a list of items into separate lists of strings, numbers, and booleans."""
    strings, numbers, booleans = [], [], []
    for v in items:
        if isinstance(v, bool):
            booleans.append(v)
        elif isinstance(v, (int, float)):
            numbers.append(v)
        elif isinstance(v, str):
            strings.append(v)
    return strings, numbers, booleans


def _build_field_expression(
    field: str, values: list[Any], delimiter: str
) -> Optional[str]:
    """Build the OData filter expression for a single expression."""
    if not values:
        return None

    has_null = None in values
    # clean and deduplicate values, excluding None and empty strings
    cleaned = list(dict.fromkeys(v for v in values if v is not None and str(v).strip()))
    if not cleaned and not has_null:
        return None

    strings, numbers, booleans = _group_by_type(cleaned)
    expressions = []
    if strings:
        escaped = [s.replace("'", "''") for s in strings]
        expressions.append(
            f"search.in({field}, '{delimiter.join(escaped)}', '{delimiter}')"
        )
    if numbers:
        expressions.append(
            f"search.in({field}, {delimiter.join(str(v) for v in numbers)}, '{delimiter}')"
        )
    if booleans:
        expressions.extend(f"{field} eq {str(b).lower()}" for b in booleans)
    if has_null:
        expressions.append(f"{field} eq null")

    if expressions:
        return f"({' or '.join(expressions)})"
    return None


def build_search_filter_from_filterable_fields(
    filterable_fields: dict[str, list[Any]],
    delimiter: Optional[str] = "|",
) -> str:
    """
    Generate an Azure AI Search filter string using AND across fields.
    Each field supports multiple values (search.in) and null checks.
    Handles string, numeric, and boolean fields with proper OData syntax.

    Args:
        filterable_fields (dict[str, list[Any]]): A dictionary where keys are field names
            and values are lists of filter values for those fields.
        delimiter (Optional[str]): Delimiter for multiple values in search.in. Defaults to "|".
    Returns:
        str: An OData filter string for Azure AI Search.
    """
    if not filterable_fields:
        return ""

    field_clauses = []
    for field, values in filterable_fields.items():
        expr = _build_field_expression(field, values, delimiter)
        if expr:
            field_clauses.append(expr)

    return merge_search_filters(field_clauses, "and")