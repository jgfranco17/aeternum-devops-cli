import re
from typing import List


def find_captured_variables(string: str) -> List[str]:
    """
    Finds and returns all substrings using captured variables.

    Args:
        string (str): The input string to search within.

    Returns:
        List[str]: A list of matched substrings in the format [a-zA-Z_].
    """
    pattern = r"\$\[([a-zA-Z_]+)\]"
    matches = re.findall(pattern, string)
    return matches
