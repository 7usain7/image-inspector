"""
PGP Extractor Module
====================
Detects and extracts ASCII-armored PGP keys, signatures, and encrypted messages.
"""

import os
import re
from typing import List, Tuple
from modules.bytes_to_ascii import bytes_to_ascii, read_image_bytes


def format_pgp_report(blocks: List[Tuple[str, str]]) -> str:
    """
    Formats the list of extracted (block_type, block_content) tuples into a clean report.
    
    :param blocks: List of tuples containing (block_type, block_content).
    :return: Formatted report string ready for terminal display.
    """
    lines = [
        "=" * 60,
        "               PGP STEGANOGRAPHY REPORT",
        "=" * 60,
    ]

    if not blocks:
        lines.append("\n[-] No PGP key blocks or messages detected in image.")
    else:
        lines.append(f"\n[+] Detected {len(blocks)} PGP Armor Block(s):")
        for idx, (b_type, _) in enumerate(blocks, 1):
            lines.append(f"    - Block #{idx}: PGP {b_type}")

        lines.append("\n[+] EXTRACTED PGP CONTENT:")
        lines.append("-" * 60)
        for _, content in blocks:
            lines.append(content)
            lines.append("")
        lines.append("-" * 60)

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def pgp_extractor(image_path: str) -> str:
    """
    Extracts PGP key blocks from an image file and returns a formatted report.
    
    :param image_path: Path to the image file.
    :return: Formatted PGP report string.
    """
    if not isinstance(image_path, str) or not os.path.isfile(image_path):
        return f"[-] Error: Image file '{image_path}' not found."

    file_bytes = read_image_bytes(image_path)
    if not file_bytes:
        return format_pgp_report([])

    file_ascii = bytes_to_ascii(file_bytes)
    if not file_ascii:
        return format_pgp_report([])

    # Single regex pass: extract (type, full_block) tuples
    pattern = r"-----BEGIN PGP (?P<type>[^-]+)-----[\s\S]*?-----END PGP (?P=type)-----"
    blocks: List[Tuple[str, str]] = [
        (m.group("type").strip(), m.group(0).strip())
        for m in re.finditer(pattern, file_ascii)
    ]

    return format_pgp_report(blocks)
