"""
Contains some utility functions that are used in the project.
"""

import re
from typing import Optional

from fundamend.models.kommunikationsrichtung import Kommunikationsrichtung


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


_UNIFIED_SEPARATOR = "/"  # how multiple Marktrollen shall be split in the kommunikation_von attribute
_ALTERNATIVE_SEPARATORS = [","]  # other separators that are used in the wild

_an_at_word_boundary = re.compile(r"\ban\b")


def _add_whitespace_before_an(original: str) -> str:
    """adds whitespace before 'an' if it is not already there"""
    return _an_at_word_boundary.sub(" an", original)


def _parse_kommunikation_von_line(kommunikation_von_line: str) -> list[Kommunikationsrichtung]:
    """
    parses a single line of kommunikation_von into a list of Kommunikationsrichtung objects
    this is necessary because some AHBs have multiple lines in the kommunikation_von attribute which must not be mixed
    """
    if not kommunikation_von_line or not kommunikation_von_line.strip():
        return []
    result: list[Kommunikationsrichtung] = []
    parts = _add_whitespace_before_an(kommunikation_von_line).split(" an ")
    if len(parts) != 2:
        # maybe this line looks different, more like 'NB an LF, MSB an NB (Gas)'
        # then we have to split at the comma first and treat each part like it was a single line. wtf
        if "," in kommunikation_von_line:
            for subpart in kommunikation_von_line.split(","):
                result += _parse_kommunikation_von_line(subpart.strip())
            return result
        raise ValueError(f"Invalid kommunikation_von string: '{kommunikation_von_line}'. Expected format: 'X an Y[/Z]'")
    sender_str = parts[0]
    receiver_str = parts[1]
    for alternative_separator in _ALTERNATIVE_SEPARATORS:
        if alternative_separator in receiver_str:
            receiver_str = receiver_str.replace(alternative_separator, _UNIFIED_SEPARATOR)
        if alternative_separator in sender_str:
            sender_str = sender_str.replace(alternative_separator, _UNIFIED_SEPARATOR)
    senders = [x.strip() for x in sender_str.split(_UNIFIED_SEPARATOR)]
    receivers = [x.strip() for x in receiver_str.split(_UNIFIED_SEPARATOR)]
    for sender in senders:
        for receiver in receivers:
            result.append(Kommunikationsrichtung(sender=sender, empfaenger=receiver))
    return result


def parse_kommunikation_von(kommunikation_von: Optional[str]) -> list[Kommunikationsrichtung] | None:
    """Splits the kommunikation_von string into something strongly typed

    Args:
        kommunikation_von: The kommunikation_von string to split, e.g. 'NB an LF/MSB'.

    Returns:
        Properly typed list of Kommunikationsrichtung objects:
        [Kommunikationsrichtung(sender='NB', empfaenger='LF'),
        Kommunikationsrichtung(sender='NB', empfaenger='MSB')]
        or none in case there are no information given (directly).
    """
    if kommunikation_von == "Beteiligte aus Ursprungs-nachricht":
        return None
    result: list[Kommunikationsrichtung] = []
    for line in (kommunikation_von or "").splitlines():
        line = line.strip()
        if line:
            result += _parse_kommunikation_von_line(line)
    return result


__all__ = ["lstrip", "rstrip", "strip", "parse_kommunikation_von"]
