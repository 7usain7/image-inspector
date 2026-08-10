"""
Bytes to ASCII Converter Module
===============================
Reads binary image data and extracts printable ASCII characters.
"""

import os
from typing import Optional


def read_image_bytes(image_path: str) -> Optional[bytes]:
    """
    Opens an image file and reads its content as raw binary bytes.
    
    :param image_path: Path to the image file.
    :return: Bytes object containing raw file data, or None if file doesn't exist.
    """
    if not os.path.isfile(image_path):
        return None

    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception:
        return None


def bytes_to_ascii(raw_bytes: bytes) -> str:
    """
    Extracts printable ASCII character sequences (including newlines and tabs)
    directly from raw data bytes.
    
    :param raw_bytes: Raw binary data (bytes).
    :return: Extracted printable ASCII string.
    """
    if not isinstance(raw_bytes, bytes):
        return ""

    # Keep printable ASCII characters (32-126) along with \n, \r, and \t
    ascii_chars = [
        chr(b) for b in raw_bytes 
        if 32 <= b <= 126 or b in (10, 13, 9)
    ]
    return "".join(ascii_chars)
