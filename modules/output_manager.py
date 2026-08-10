"""
Output Management Module
========================
Formats findings and writes output to specified destination files.
"""

from typing import Optional


def save_output(data: str, filename: Optional[str] = None) -> None:
    """Prints results to stdout and saves to file if filename is provided."""
    print(data)
    if filename:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(data + "\n")
            print(f"Data Saved in {filename}")
        except IOError as e:
            print(f"Error saving data to {filename}: {e}")
