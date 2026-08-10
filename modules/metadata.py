"""
Metadata Extraction Module
==========================
Extracts Date & Time, Device Information, and Geolocation metadata from image files.
"""

import os
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags
from modules.gps_parser import parse_gps_info


def _clean_value(val: Any) -> Any:
    """Convert bytes or raw values into clean string representations."""
    if isinstance(val, bytes):
        try:
            return val.decode("utf-8", errors="replace").strip("\x00").strip()
        except Exception:
            return str(val)
    return val


def _extract_raw_exif(img: Image.Image) -> Tuple[Dict[str, Any], Dict[int, Any]]:
    """Extract named EXIF tags and raw GPS IFD dictionary."""
    named_tags: Dict[str, Any] = {}
    gps_ifd: Dict[int, Any] = {}

    exif_data = img.getexif()
    if not exif_data:
        return named_tags, gps_ifd

    # 0th IFD
    for tag_id, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        named_tags[tag_name] = _clean_value(value)

    # Sub-IFDs (Exif, GPSInfo)
    for ifd_id in ExifTags.IFD:
        try:
            ifd = exif_data.get_ifd(ifd_id)
            if not ifd:
                continue
            if ifd_id == ExifTags.IFD.GPSInfo:
                gps_ifd = ifd
            elif ifd_id == ExifTags.IFD.Exif:
                for k, v in ifd.items():
                    tag_name = ExifTags.TAGS.get(k, str(k))
                    named_tags[tag_name] = _clean_value(v)
        except Exception:
            pass

    return named_tags, gps_ifd


def _parse_date_time(tags: Dict[str, Any], gps_data: Dict[str, Any]) -> Dict[str, str]:
    """Parse all date and time related metadata."""
    dt_info: Dict[str, str] = {}

    date_original = tags.get("DateTimeOriginal")
    offset_original = tags.get("OffsetTimeOriginal") or tags.get("OffsetTime")
    subsec_original = tags.get("SubsecTimeOriginal")

    if date_original:
        full_ts = str(date_original)
        if subsec_original:
            full_ts += f".{subsec_original}"
        if offset_original:
            full_ts += f" (UTC{offset_original})"
        dt_info["Date & Time Taken"] = full_ts
        dt_info["Raw Date Taken"] = str(date_original)

    if offset_original:
        dt_info["Timezone Offset"] = str(offset_original)

    date_digitized = tags.get("DateTimeDigitized")
    if date_digitized and date_digitized != date_original:
        dt_info["Date & Time Digitized"] = str(date_digitized)

    date_modified = tags.get("DateTime")
    if date_modified:
        dt_info["Date & Time Modified"] = str(date_modified)

    if "gps_timestamp_utc" in gps_data:
        dt_info["GPS UTC Timestamp"] = gps_data["gps_timestamp_utc"]

    return dt_info


def _parse_device_info(tags: Dict[str, Any]) -> Dict[str, str]:
    """Parse device hardware, software, lens, and owner metadata."""
    device: Dict[str, str] = {}

    field_map = [
        ("Make", "Camera Make"),
        ("Model", "Camera Model"),
        ("Software", "Software / Firmware"),
        ("HostComputer", "Host Computer"),
        ("LensModel", "Lens Model"),
        ("LensMake", "Lens Make"),
        ("BodySerialNumber", "Device Serial Number"),
        ("SerialNumber", "Device Serial Number"),
        ("CameraSerialNumber", "Device Serial Number"),
        ("LensSerialNumber", "Lens Serial Number"),
        ("Artist", "Artist / Author"),
        ("XPAuthor", "Artist / Author"),
        ("CameraOwnerName", "Camera Owner"),
        ("OwnerName", "Camera Owner"),
        ("Copyright", "Copyright"),
    ]

    for exif_key, label in field_map:
        val = tags.get(exif_key)
        if val and label not in device:
            device[label] = str(val)

    if "MakerNote" in tags and "Apple" in str(tags.get("Make", "")):
        device["MakerNote"] = "Apple iOS MakerNote metadata present"

    return device


def _format_report(
    file_info: Dict[str, str],
    date_time: Dict[str, str],
    device_info: Dict[str, str],
    geo: Dict[str, Any],
) -> str:
    """Format extracted information into a clean terminal report string."""
    lines = [
        "=" * 60,
        "                IMAGE INSPECTOR REPORT",
        "=" * 60,
        "\n[+] FILE INFORMATION",
        f"    File Name   : {file_info.get('file_name', 'N/A')}",
        f"    File Size   : {file_info.get('file_size', 'N/A')}",
        f"    Format      : {file_info.get('format', 'N/A')}",
        f"    Dimensions  : {file_info.get('dimensions', 'N/A')}",
        "\n[+] DATE & TIME",
    ]

    if date_time:
        for k, v in date_time.items():
            lines.append(f"    {k:<22}: {v}")
    else:
        lines.append("    No date/time metadata found.")

    lines.append("\n[+] DEVICE USED & OWNER INFO")
    if device_info:
        for k, v in device_info.items():
            lines.append(f"    {k:<22}: {v}")
    else:
        lines.append("    No device/owner metadata found.")

    lines.append("\n[+] GEOLOCATION (GPS)")
    if geo and ("decimal_coordinates" in geo or "latitude_dd" in geo):
        if "dms_coordinates" in geo:
            lines.append(f"    DMS Coordinates       : {geo['dms_coordinates']}")
        if "decimal_coordinates" in geo:
            lines.append(f"    Decimal Coordinates   : {geo['decimal_coordinates']}")
        if "altitude" in geo:
            lines.append(f"    Altitude              : {geo['altitude']}")
        if "speed" in geo:
            lines.append(f"    Speed                 : {geo['speed']}")
        if "direction" in geo:
            lines.append(f"    Direction / Heading   : {geo['direction']}")
        if "google_maps_url" in geo:
            lines.append(f"    Google Maps           : {geo['google_maps_url']}")
        if "openstreetmap_url" in geo:
            lines.append(f"    OpenStreetMap         : {geo['openstreetmap_url']}")
    else:
        lines.append("    No GPS geolocation metadata found in this image.")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def extract_metadata(image_path: str) -> Optional[str]:
    """
    Main metadata extraction function.
    Reads an image file and returns the formatted metadata report string.
    """
    if not os.path.isfile(image_path):
        return f"[-] Error: Image file '{image_path}' not found."

    try:
        with Image.open(image_path) as img:
            file_info = {
                "file_name": os.path.basename(image_path),
                "file_size": f"{os.path.getsize(image_path):,} bytes",
                "format": img.format or "Unknown",
                "dimensions": f"{img.width} x {img.height} px",
            }

            named_tags, gps_ifd = _extract_raw_exif(img)
            geo = parse_gps_info(gps_ifd, ExifTags.GPSTAGS) if gps_ifd else {}
            date_time = _parse_date_time(named_tags, geo)
            device_info = _parse_device_info(named_tags)

            return _format_report(file_info, date_time, device_info, geo)

    except Exception as e:
        return f"[-] Error extracting metadata from '{image_path}': {e}"
