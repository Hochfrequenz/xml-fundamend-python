"""
Contains some utility functions that are used in the project.
"""


def lstrip(prefix: str, text: str) -> str:
    """Strip the given prefix from the given text. If the text does not start with the prefix, return the text as is.

    Args:
        prefix: The prefix to strip.
        text: The text to strip the prefix from.

    Returns:
        The text with the prefix stripped.
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def rstrip(text: str, suffix: str) -> str:
    """Strip the given suffix from the given text. If the text does not end with the suffix, return the text as is.

    Args:
        text: The text to strip the suffix from.
        suffix: The suffix to strip.

    Returns:
        The text with the suffix stripped.
    """
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def strip(prefix: str, text: str, suffix: str) -> str:
    """Strip the given prefix and suffix from the given text. If the text does not start with the prefix or does not
    end with the suffix, return the text as is.

    Args:
        prefix: The prefix to strip.
        text: The text to strip the prefix from.
        suffix: The suffix to strip.

    Returns:
        The text with the prefix and suffix stripped.
    """
    return lstrip(prefix, rstrip(text, suffix))
