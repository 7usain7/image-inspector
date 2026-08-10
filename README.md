# Image Inspector

**Image Inspector** is a multi-functional digital image forensics, passive OSINT reconnaissance, and steganography analysis tool built in Python. It enables cybersecurity professionals, digital forensic investigators, and security researchers to inspect images, extract EXIF/GPS metadata, recover embedded cryptographic keys, and visualize findings through both a **Command-Line Interface (CLI)** and an **interactive Desktop GUI**.

---

## Features

- **📅 Date & Time Forensics (`-m`)**: Extracts original capture timestamps, subsecond precision (`SubsecTimeOriginal`), timezone offsets (`OffsetTimeOriginal`), file modification dates, and satellite GPS UTC timestamps.
- **📱 Device & Hardware Intelligence (`-m`)**: Identifies camera manufacturer, device model, operating system/software version, lens specifications, host computer, body/lens serial numbers, creator/copyright information, and Apple iOS MakerNotes.
- **📍 Geolocation & Mapping (`-m`)**: Converts EXIF Degrees/Minutes/Seconds (DMS) rational coordinates to Decimal Degrees (DD), extracts altitude, speed, and heading, and generates direct clickable **Google Maps** and **OpenStreetMap** links.
- **🔐 Cryptographic Key & Steganography Extraction (`-s`)**: Scans binary image streams and extracts embedded:
  - **OpenPGP Blocks**: Public keys, private keys, signed messages, and signatures.
  - **OpenSSH Private Keys**: Modern `-----BEGIN OPENSSH PRIVATE KEY-----` formats.
  - **PEM Private Keys**: RSA, DSA, EC, PKCS#8, and encrypted private keys.
  - **OpenSSH Public Keys**: Single-line `ssh-ed25519`, `ssh-rsa`, `ecdsa-sha2-*`, and `sk-*` public keys.
  - **RFC 4716 Public Keys & X.509 Certificates**.
- **🖥️ Modern Desktop GUI (`-g` / `gui.py`)**: A dark-themed graphical interface featuring live scaled image previews, tabbed analysis views, one-click map launchers, and clipboard/file export controls.
- **💾 Output Management (`-o`)**: Formats findings clearly on standard output and exports clean forensic reports to disk.

---

## Prerequisites

- **Python**: Version `3.8` or higher installed.
- **Dependencies**: `Pillow` (for image loading and EXIF parsing) and `tkinter` (for the graphical interface).

---

## Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/7usain7/image-inspector.git
   cd image-inspector
   ```

2. **Set up a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Command-Line Interface (CLI)

Run `imageinspector.py` with `--help` to view all available options:

```bash
python3 imageinspector.py --help
```

### CLI Command Options

| Flag                    | Argument     | Description                                                             |
| :---------------------- | :----------- | :---------------------------------------------------------------------- |
| `-m`, `--metadata`      | None         | Extract metadata from the image (Date & Time, Device Used, Geolocation) |
| `-s`, `--steganography` | None         | Detect and extract hidden cryptographic keys (PGP, SSH, PEM)            |
| `-g`, `--gui`           | None         | Launch the graphical user interface (GUI)                               |
| `-o`, `--output`        | `"FileName"` | Specify output filename to save report                                  |
| `image`                 | `path`       | Path to the image file to inspect                                       |

---

## CLI Examples

### 1. Extract EXIF, Device Info & GPS Coordinates

```bash
python3 imageinspector.py -m image-examples/test1.JPG
```

**Output**:

```text
============================================================
              WELCOME TO IMAGE INSPECTOR
============================================================
============================================================
                IMAGE INSPECTOR REPORT
============================================================

[+] FILE INFORMATION
    File Name   : test1.JPG
    File Size   : 1,264,009 bytes
    Format      : JPEG
    Dimensions  : 3840 x 2160 px

[+] DATE & TIME
    Date & Time Taken     : 2026:08:08 17:41:08.023 (UTC+03:00)
    Raw Date Taken        : 2026:08:08 17:41:08
    Timezone Offset       : +03:00
    Date & Time Modified  : 2026:08:08 17:41:08

[+] DEVICE USED & OWNER INFO
    Camera Make           : Apple
    Camera Model          : iPhone 16
    Software / Firmware   : 26.5.2
    Host Computer         : iPhone 16
    Lens Model            : iPhone 16 back dual wide camera 5.96mm f/1.6
    Lens Make             : Apple
    MakerNote             : Apple iOS MakerNote metadata present

[+] GEOLOCATION (GPS)
    No GPS geolocation metadata found in this image.

============================================================
```

---

### 2. Extract Geolocation with Direct Map Links

```bash
python3 imageinspector.py -m image-examples/image-example1.jpeg
```

**Output**:

```text
[+] GEOLOCATION (GPS)
    DMS Coordinates       : 32° 5' 11.87" N, 34° 53' 6.47" E
    Decimal Coordinates   : 32.08663, 34.885131
    Google Maps           : https://maps.google.com/?q=32.08663,34.885131
    OpenStreetMap         : https://www.openstreetmap.org/?mlat=32.08663&mlon=34.885131#map=16/32.08663/34.885131
```

---

### 3. Extract Embedded Steganography Keys (PGP & SSH)

```bash
python3 imageinspector.py -s -o keys_report.txt image-examples/image-example2.jpeg
```

**Output**:

```text
============================================================
         KEY & STEGANOGRAPHY EXTRACTION REPORT
============================================================

[+] Detected 1 Cryptographic Key / Armor Block(s):
    - Key #1: [PGP] PGP PUBLIC KEY BLOCK

[+] EXTRACTED KEYS & CONTENT:
------------------------------------------------------------
-----BEGIN PGP PUBLIC KEY BLOCK-----
xo0EZuV9/AEEANRklh3ULNznRPlFsEfbWGMPp1RemjmNBFHviWRdOiQMrrG5CeDY
...
-----END PGP PUBLIC KEY BLOCK-----
------------------------------------------------------------

============================================================
Data Saved in keys_report.txt
```

---

## Graphical User Interface (GUI)

You can launch the interactive desktop interface using either:

```bash
# Standalone launcher
python3 gui.py

# Or via CLI flag
python3 imageinspector.py -g
```

### GUI Features:

- **Live Scaled Thumbnail Preview**: Displays the image with aspect ratio preservation alongside file format, dimensions, and size.
- **Tabbed Analysis**:
  - **Metadata Tab**: Organized Date/Time, Device, and Geolocation cards with **Open in Google Maps** and **Open in OpenStreetMap** buttons.
  - **Keys Tab**: Detects and displays PGP and SSH keys with a **Copy Key** and **Save Key (.asc)** button.
  - **Report Tab**: Complete monospace analysis report with **Copy** and **Export (.txt)** options.

---

## Project Structure

```text
image-inspector/
├── gui.py                      # Standalone GUI launcher
├── imageinspector.py           # Main CLI & GUI entrypoint
├── README.md                   # Project documentation
├── requirements.txt            # Project dependencies
├── LICENSE                     # License terms
├── image-examples/             # Sample images for testing (GPS, PGP, EXIF)
└── modules/
    ├── __init__.py             # Package initializer
    ├── bytes_to_ascii.py       # Raw binary byte extraction & ASCII filter
    ├── gps_parser.py           # DMS to Decimal conversion & map link generator
    ├── gui.py                  # Tkinter desktop application
    ├── key_extractor.py        # PGP, OpenSSH, and PEM key extraction
    ├── metadata.py             # EXIF, timestamp, and device metadata parser
    └── output_manager.py       # Terminal formatting and report export
```

---

## License

This project is proprietary. The code is publicly visible for portfolio and viewing purposes only. No unauthorized copying, modification, or distribution is permitted. See [License](LICENSE) for details.
