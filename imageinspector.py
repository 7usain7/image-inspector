#!/usr/bin/env python3
"""
Image Inspector CLI & GUI Tool
==============================
A multi-functional passive reconnaissance and image analysis tool.

Usage:
    image-inspector -m "metadata" [-o output_file] <image_path>
    image-inspector -s "steganography" [-o output_file] <image_path>
    image-inspector -g (launch GUI interface)
"""

import argparse
import sys

from modules.metadata import extract_metadata
from modules.output_manager import save_output
from modules.key_extractor import key_extractor

WELCOME_MESSAGE = """
Welcome to Image Inspector
"""


def main():
    parser = argparse.ArgumentParser(
        prog="image-inspector",
        description="Welcome to Image Inspector\n\nA multi-functional passive reconnaissance tool.",
        add_help=True,
    )

    parser.add_argument("-m", "--metadata", action="store_true", help="Extract metadata from the image (e.g., geolocation, device info)")
    parser.add_argument("-s", "--steganography", action="store_true", help="Detect and extract hidden cryptographic keys (PGP, SSH, PEM)")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch the graphical user interface (GUI)")
    parser.add_argument("-o", "--output", metavar='"FileName"', help="Specify the file name to save output")
    parser.add_argument("image", nargs="?", help="Path to the image file to inspect")

    if len(sys.argv) == 1:
        print(WELCOME_MESSAGE)
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.gui:
        from modules.gui import launch_gui
        launch_gui()
        sys.exit(0)

    if not args.image:
        print("Error: Please provide an image path or run with -g to launch GUI.")
        parser.print_help()
        sys.exit(1)

    if not (args.metadata or args.steganography):
        print("Error: Please specify at least one option (-m, -s, or -g).")
        parser.print_help()
        sys.exit(1)

    print(WELCOME_MESSAGE)

    results = []

    if args.metadata:
        res = extract_metadata(args.image)
        if res:
            results.append(res)

    if args.steganography:
        res = key_extractor(args.image)
        if res:
            results.append(res)

    if results:
        formatted_data = "\n\n".join(results)
        save_output(formatted_data, args.output)


if __name__ == "__main__":
    main()
