"""
GPS Parser Module
=================
Handles conversion and formatting of EXIF GPS coordinates and metadata.
"""

from typing import Dict, Any, Optional, Tuple


def _convert_dms_to_dd(dms_values: Tuple[Any, Any, Any], ref: str) -> Optional[float]:
    """
    Convert (Degrees, Minutes, Seconds) tuple and Reference direction to Decimal Degrees.
    """
    try:
        deg = float(dms_values[0])
        minutes = float(dms_values[1])
        sec = float(dms_values[2])
        dd = deg + (minutes / 60.0) + (sec / 3600.0)
        if ref.upper() in ["S", "W"]:
            dd = -dd
        return round(dd, 6)
    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return None


def _format_dms(dms_values: Tuple[Any, Any, Any], ref: str) -> Optional[str]:
    """
    Format (Degrees, Minutes, Seconds) to human-readable DMS string (e.g. 32° 5' 11.87\" N).
    """
    try:
        deg = int(dms_values[0])
        minutes = int(dms_values[1])
        sec = float(dms_values[2])
        return f"{deg}° {minutes}' {sec:.2f}\" {ref.upper()}"
    except (TypeError, ValueError, IndexError):
        return None


def parse_gps_info(gps_ifd: Dict[int, Any], gpstags: Dict[int, str]) -> Dict[str, Any]:
    """
    Parse raw GPS IFD dictionary into structured and human-readable GPS information.
    """
    gps_data: Dict[str, Any] = {}
    named_gps: Dict[str, Any] = {}

    for tag_id, value in gps_ifd.items():
        tag_name = gpstags.get(tag_id, str(tag_id))
        named_gps[tag_name] = value

    lat_dms = named_gps.get("GPSLatitude")
    lat_ref = named_gps.get("GPSLatitudeRef")
    lon_dms = named_gps.get("GPSLongitude")
    lon_ref = named_gps.get("GPSLongitudeRef")

    if lat_dms and lat_ref and lon_dms and lon_ref:
        lat_ref_str = str(lat_ref).strip().upper()
        lon_ref_str = str(lon_ref).strip().upper()

        lat_dd = _convert_dms_to_dd(lat_dms, lat_ref_str)
        lon_dd = _convert_dms_to_dd(lon_dms, lon_ref_str)

        lat_dms_str = _format_dms(lat_dms, lat_ref_str)
        lon_dms_str = _format_dms(lon_dms, lon_ref_str)

        if lat_dd is not None and lon_dd is not None:
            gps_data["latitude_dd"] = lat_dd
            gps_data["longitude_dd"] = lon_dd
            gps_data["decimal_coordinates"] = f"{lat_dd}, {lon_dd}"
            gps_data["dms_coordinates"] = f"{lat_dms_str}, {lon_dms_str}"
            gps_data["google_maps_url"] = f"https://maps.google.com/?q={lat_dd},{lon_dd}"
            gps_data["openstreetmap_url"] = f"https://www.openstreetmap.org/?mlat={lat_dd}&mlon={lon_dd}#map=16/{lat_dd}/{lon_dd}"

    # Altitude
    altitude = named_gps.get("GPSAltitude")
    altitude_ref = named_gps.get("GPSAltitudeRef", 0)
    if altitude is not None:
        try:
            alt_val = float(altitude)
            ref_desc = "below sea level" if altitude_ref == 1 else "above sea level"
            gps_data["altitude"] = f"{alt_val:.2f} m ({ref_desc})"
        except (ValueError, TypeError):
            pass

    # Speed
    speed = named_gps.get("GPSSpeed")
    speed_ref = named_gps.get("GPSSpeedRef", "K")
    if speed is not None:
        try:
            unit_map = {"K": "km/h", "M": "mph", "N": "knots"}
            unit = unit_map.get(str(speed_ref).upper(), str(speed_ref))
            gps_data["speed"] = f"{float(speed):.2f} {unit}"
        except (ValueError, TypeError):
            pass

    # Direction / Heading
    img_dir = named_gps.get("GPSImgDirection")
    img_dir_ref = named_gps.get("GPSImgDirectionRef", "T")
    if img_dir is not None:
        try:
            dir_type = "True North" if str(img_dir_ref).upper() == "T" else "Magnetic North"
            gps_data["direction"] = f"{float(img_dir):.2f}° ({dir_type})"
        except (ValueError, TypeError):
            pass

    # GPS Timestamp (Satellite UTC)
    gps_date = named_gps.get("GPSDateStamp")
    gps_time = named_gps.get("GPSTimeStamp")
    if gps_date and gps_time:
        try:
            h = int(gps_time[0])
            m = int(gps_time[1])
            s = float(gps_time[2])
            gps_data["gps_timestamp_utc"] = f"{gps_date} {h:02d}:{m:02d}:{s:05.2f} UTC"
        except (IndexError, ValueError, TypeError):
            if gps_date:
                gps_data["gps_timestamp_utc"] = str(gps_date)
    elif gps_date:
        gps_data["gps_timestamp_utc"] = str(gps_date)

    return gps_data
