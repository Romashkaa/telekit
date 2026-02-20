from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent  # telekit/


def format_file_size(size: int, precision: int = 1) -> str:
    """
    Convert a file size in bytes to a human-readable string using
    the binary unit system (1 KB = 1024 bytes).

    The function automatically selects the appropriate unit
    (B, KB, MB, GB, TB, PB) and formats the number according
    to the specified precision. Trailing zeros are removed.

    :param size: File size in bytes. Must be a non-negative integer.
    :type size: `int`

    :param precision: Number of decimal places to keep for fractional
        values. Ignored if the value is an integer after conversion.
        Default is 1.
    :type precision: `int`

    :raises ValueError: If ``size`` is negative.

    :return: Human-readable file size string.
    :rtype: `str`

    Examples:

    Basic usage:
        >>> format_file_size(500)
        '500 B'

        >>> format_file_size(2048)
        '2 KB'

        >>> format_file_size(1048576)
        '1 MB'

    Using precision:
        >>> format_file_size(1545, precision=2)
        '1.51 KB'

        >>> format_file_size(1600, precision=3)
        '1.562 KB'

        >>> format_file_size(123456789, precision=1)
        '117.7 MB'

    Large values:
        >>> format_file_size(1099511627776)
        '1 TB'
    """

    _size: int | float = size

    if _size < 0:
        raise ValueError("Size must be non-negative")

    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    if _size == 0:
        return "0 B"

    index = 0
    _size = float(_size)

    while _size >= 1024 and index < len(units) - 1:
        _size /= 1024
        index += 1

    if _size.is_integer():
        formatted = f"{int(_size)}"
    else:
        formatted = f"{_size:.{precision}f}".rstrip("0").rstrip(".")

    return f"{formatted} {units[index]}"