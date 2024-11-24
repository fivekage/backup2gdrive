def human_readable_bytes(byte_value):
    """
    Convert bytes into a human-readable format (KB, MB, GB, TB).
    """
    # Define units in ascending order
    units = ["B", "KB", "MB", "GB", "TB"]
    # Start with bytes
    size = byte_value
    unit_index = 0
    # Iterate through the units, converting the byte value to the next unit
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"
