def fts_prefix_query(query: str) -> str:
    """
    Convert user query into a prefix search for FTS5.
    Example: "Munich ride" -> "Munich* ride*"
    """
    return " ".join(f"{word}*" for word in query.split())