"""
Key Extractor Module
====================
Detects and extracts PGP and SSH keys, certificates, and encrypted blocks
from image binary data (steganography analysis).
"""

import os
import re
from typing import List, Tuple
from modules.bytes_to_ascii import bytes_to_ascii, read_image_bytes


def extract_keys(image_path: str) -> List[Tuple[str, str, str]]:
    """
    Extracts PGP and SSH keys/blocks from an image file.
    
    :param image_path: Path to the target image file.
    :return: List of (category, key_type, full_content) tuples.
    """
    if not isinstance(image_path, str) or not os.path.isfile(image_path):
        return []

    file_bytes = read_image_bytes(image_path)
    if not file_bytes:
        return []

    file_ascii = bytes_to_ascii(file_bytes)
    if not file_ascii:
        return []

    found_keys: List[Tuple[str, str, str]] = []

    # 1. Standard 5-dash PEM / OpenPGP / OpenSSH / RSA / DSA / EC Armored Blocks
    armor_pattern = r"-----BEGIN (?P<type>[A-Z0-9 ]+)-----[\s\S]*?-----END (?P=type)-----"
    for match in re.finditer(armor_pattern, file_ascii):
        raw_type = match.group("type").strip()
        content = match.group(0).strip()

        if "PGP" in raw_type:
            category = "PGP"
            display_type = raw_type
        elif "OPENSSH" in raw_type or "SSH" in raw_type or "PRIVATE KEY" in raw_type:
            category = "SSH"
            display_type = raw_type
        elif "CERTIFICATE" in raw_type:
            category = "CERTIFICATE"
            display_type = raw_type
        else:
            category = "PEM / KEY"
            display_type = raw_type

        found_keys.append((category, display_type, content))

    # 2. RFC 4716 SSH2 Public Keys (4 dashes)
    ssh2_pattern = r"---- BEGIN SSH2 PUBLIC KEY ----[\s\S]*?---- END SSH2 PUBLIC KEY ----"
    for match in re.finditer(ssh2_pattern, file_ascii):
        found_keys.append(("SSH", "SSH2 Public Key (RFC 4716)", match.group(0).strip()))

    # 3. OpenSSH Single-line Public Keys (ssh-rsa, ssh-ed25519, ecdsa, etc.)
    ssh_pub_pattern = (
        r"(?:ssh-rsa|ssh-dss|ssh-ed25519|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|"
        r"ecdsa-sha2-nistp521|sk-ssh-ed25519@openssh\.com|sk-ecdsa-sha2-nistp256@openssh\.com)"
        r"\s+[A-Za-z0-9+/=]{20,}(?:[ \t]+[a-zA-Z0-9_.@\-+=/]+)?"
    )
    for match in re.finditer(ssh_pub_pattern, file_ascii):
        content = match.group(0).strip()
        # Avoid duplicate detection if already inside an armor block
        if not any(content in existing[2] for existing in found_keys):
            key_algo = content.split()[0]
            found_keys.append(("SSH", f"OpenSSH Public Key ({key_algo})", content))

    return found_keys


def format_key_report(keys: List[Tuple[str, str, str]]) -> str:
    """
    Formats extracted cryptographic keys into a clean terminal report string.
    
    :param keys: List of (category, key_type, full_content) tuples.
    :return: Formatted report string.
    """
    lines = [
        "=" * 60,
        "         KEY & STEGANOGRAPHY EXTRACTION REPORT",
        "=" * 60,
    ]

    if not keys:
        lines.append("\n[-] No PGP, SSH, or PEM cryptographic keys detected in image.")
    else:
        lines.append(f"\n[+] Detected {len(keys)} Cryptographic Key / Armor Block(s):")
        for idx, (category, k_type, _) in enumerate(keys, 1):
            lines.append(f"    - Key #{idx}: [{category}] {k_type}")

        lines.append("\n[+] EXTRACTED KEYS & CONTENT:")
        lines.append("-" * 60)
        for _, _, content in keys:
            lines.append(content)
            lines.append("")
        lines.append("-" * 60)

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def key_extractor(image_path: str) -> str:
    """
    Extracts PGP and SSH keys from an image file and returns a formatted report.
    
    :param image_path: Path to the image file.
    :return: Formatted key report string.
    """
    if not isinstance(image_path, str) or not os.path.isfile(image_path):
        return f"[-] Error: Image file '{image_path}' not found."

    keys = extract_keys(image_path)
    return format_key_report(keys)


# Backwards compatibility aliases
extract_pgp_blocks = extract_keys
format_pgp_report = format_key_report
pgp_extractor = key_extractor
