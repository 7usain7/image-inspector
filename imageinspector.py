#!/usr/bin/env python3
"""
Image Inspector CLI Tool
========================
A multi-functional image analysis tool.

Usage:
    image-inspector -m "metadata" [-o output_file] <image_path>
    image-inspector -s "steganography" [-o output_file] <image_path>
"""

import sys
import argparse

WELCOME_MESSAGE = """
Welcome to Image Inspector
"""

def main():
    parser = argparse.ArgumentParser(
        prog="image-inspector",
        description="Welcome to Image Inspector\n\nA multi-functional passive reconnaissance tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="Show this help message and exit"
    )
    parser.add_argument(
        "-m", "--metadata",
        action="store_true",
        help="Extract metadata from the image (e.g., geolocation, device info)"
    )
    parser.add_argument(
        "-s", "--steganography",
        action="store_true",
        help="Detect and extract hidden data from the image using steganography techniques"
    )
    parser.add_argument(
        "-o", "--output",
        metavar='"FileName"',
        type=str,
        help="Specify the file name to save output"
    )
    parser.add_argument(
        "image",
        nargs="?",
        help="Path to the image file to inspect"
    )

    args = parser.parse_args()

    print(WELCOME_MESSAGE)
    

if __name__ == "__main__":
    main()
