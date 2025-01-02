# /utils/general_utils.py
# Author: Indrajit Ghosh
# Created On: Jun 16, 2024
#
import string
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import pytz
from tzlocal import get_localzone_name

def sha256_hash(data: str):
    """
    Creates a SHA-256 hash of the input data.

    Args:
        data (str): The input data to be hashed. Can be a string or bytes.

    Returns:
        str: The SHA-256 hash of the input data in hexadecimal format.
    """
    if isinstance(data, bytes):
        sha256_hash = hashlib.sha256(data).hexdigest()
    else:
        sha256_hash = hashlib.sha256(data.encode()).hexdigest()
    return sha256_hash

def get_system_timezone():
    """
    Get the system's current timezone.

    Returns:
        str: The system's timezone, or None if it cannot be determined.
    """
    try:
        # Get the local timezone name using tzlocal
        local_tz_name = get_localzone_name()
        return local_tz_name
    except Exception as e:
        # Log the exception if needed
        return None

def utcnow():
    """
    Get the current UTC datetime.

    Returns:
        datetime: A datetime object representing the current UTC time.
    """
    return datetime.now(timezone.utc)

def get_timezone_offset(timezone_str):
    """
    Get the UTC offset for a given timezone string.

    Args:
        timezone_str (str): The timezone string.

    Returns:
        timedelta: The offset of the given timezone from UTC.
    """
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        offset = now.utcoffset()
        return offset
    except Exception as e:
        # Log the exception if needed
        return timedelta(0)  # Default to UTC offset

def convert_utc_to_local_str(dt, show_time: bool = True, weekday: bool = True):
    """
    Convert a datetime object with timezone information UTC to a string representation in local time format.

    Args:
        dt (datetime.datetime): A datetime object with timezone information UTC.
        show_time (bool, optional): Whether to include the time in the output string. Defaults to True.
        weekday (bool, optional): Whether to include the weekday in the output string. Defaults to True.

    Returns:
        str: A string representation of the datetime object in local time format.
    """
    timezone_str = get_system_timezone()

    # Get the offset for the given timezone
    offset = get_timezone_offset(timezone_str)

    # Check whether the offset found or not
    timezone_str = 'UTC' if offset == timedelta(0) else timezone_str
    
    # Convert UTC to local time
    dt_local = dt + offset

    # Format the datetime object
    local_format = ""
    if weekday:
        local_format += dt_local.strftime("%a, ")
    local_format += dt_local.strftime("%d %b %Y")
    if show_time:
        local_format += dt_local.strftime(f" %I:%M %p ({timezone_str})")

    return local_format