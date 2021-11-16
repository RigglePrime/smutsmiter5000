def replace_mul(s: str, *args: tuple[str, str]) -> str:
    """Perform many string replacements at once

    Arguments:
        s (str): the string to perform replacements on
        args (*tuple[str, str]): tuples in the form of ("prev_value", "desired_value")
    
    Returns a string on which the replacements were performed on
    """
    for old, new in args:
        s = s.replace(old, new)
    return s
