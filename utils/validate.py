import re


def validate_filename(filename: str) -> bool:
    """
    Validate a filename by checking if it contains any invalid characters or if it is equal to its own base name (i.e., it is a directory).

    Parameters
    ----------
    filename : str
        The filename to validate.

    Returns
    -------
    bool
        True if the filename is valid, False otherwise.
    """
    return isinstance(filename, str) and not any(c in filename for c in r'<>:"/\|?*')


def validate_regex(regex: str) -> bool:
    """
    Validate a regex by attempting to compile it. If compilation fails, return False, otherwise return True.

    Parameters
    ----------
    regex : str
        The regex to validate.

    Returns
    -------
    bool
        True if the regex is valid, False otherwise.
    """
    try:
        re.compile(regex)
        return True
    except re.error:
        return False


def validate_path(path: str) -> bool:
    """
    Validate a path by checking if it is a string that contains a directory and a filename.

    Parameters
    ----------
    path : str
        The path to validate.

    Returns
    -------
    bool
        True if the path is valid, False otherwise.
    """
    REGEX_PATH_MULTI_OS = (
        r"^(?:[a-zA-Z]:[\\/]|[\\/])?(?:[^<>:|?*\r\n]+[\\/])*[^<>:|?*\r\n]*[\\/]?$"
    )
    return isinstance(path, str) and re.match(REGEX_PATH_MULTI_OS, path) is not None
