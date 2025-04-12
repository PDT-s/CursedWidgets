import curses
from ..constants import AlignmentOptions, OrientationOptions


def add_str_no_overflows(
    window: curses.window,
    line: int,
    col: int,
    string: str,
    extra_lines: int = 0,
    alignment: AlignmentOptions = AlignmentOptions.LEFT,
    attr=None,
) -> int:
    """
    Add a string to a window without overflowing the window.
    If the string is too long, it will be split into multiple lines.
    If alignment is not set to AlignmentOptions.MANUAL, the col
    parameter will be ignored.

    Parameters
    ----------
    window : curses.window
        The window where the string will be added.
    line : int
        The line where the string will be added.
    col : int
        The column where the string will be added.
    string : str
        The string to be added.
    extra_lines : int, optional
        The number of extra lines that can be used
        in case that the string is splitted, by default 0
    alignment : AlignmentOptions, optional
        The alignment of the line, by default AlignmentOptions.LEFT
    attr: int
        The attributes to add the string.

    Returns
    -------
    int
        The next line where a string can be added.
    """

    available_cols = window.getmaxyx()[1] - 2
    # If the alignment is manual, there will be some margin left
    # so the available columns may not be the same as the window's width
    if alignment == AlignmentOptions.MANUAL:
        available_cols -= col

    # Add the string to the window
    add_str_align(window, line, col, string[:available_cols], alignment, attr)
    while len(string) > available_cols and extra_lines > 0:
        # If no more lines can be added, break
        if line + 1 >= window.getmaxyx()[0] - extra_lines:
            break
        string = string[available_cols:]  # string remainder not added
        line += 1  # next line
        extra_lines -= 1
        # Add the string to the window
        add_str_align(window, line, col, string[:available_cols], alignment, attr)
    return line + 1


def _add_str_centered(window: curses.window, line: int, string: str, attr=None) -> None:
    """
    Add a string to a window centered horizontally.

    Parameters
    ----------
    window : curses.window
        The window where the string will be added.
    line : int
        The line where the string will be added.
    string : str
        The string to be added.
    attr: int
        The attributes to add the string.
    """
    col = (window.getmaxyx()[1] - len(string)) // 2
    if attr is not None:
        window.addstr(line, col, string, attr)
    else:
        window.addstr(line, col, string)


def _add_str_right(window: curses.window, line: int, string: str, attr=None) -> None:
    """
    Add a string to a window aligned to the right.

    Parameters
    ----------
    window : curses.window
        The window where the string will be added.
    line : int
        The line where the string will be added.
    string : str
        The string to be added.
    attr: int
        The attributes to add the string.
    """
    col = window.getmaxyx()[1] - len(string) - 1
    if attr is not None:
        window.addstr(line, col, string, attr)
    else:
        window.addstr(line, col, string)


def _add_str_left(window: curses.window, line: int, string: str, attr=None) -> None:
    """
    Add a string to a window aligned to the left.

    Parameters
    ----------
    window : curses.window
        The window where the string will be added.
    line : int
        The line where the string will be added.
    string : str
        The string to be added.
    attr: int
        The attributes to add the string.
    """
    if attr is not None:
        window.addstr(line, 1, string, attr)
    else:
        window.addstr(line, 1, string)


def add_str_align(
    window: curses.window,
    line: int,
    col: int,
    string: str,
    alignment: AlignmentOptions,
    attr=None,
) -> None:
    """
    Add a string to a window with a specific alignment.
    The column will only be used if the alignment is set to AlignmentOptions.MANUAL.

    Parameters
    ----------
    window : curses.window
        The window where the string will be added.
    line : int
        The line where the string will be added.
    col : int
        The column where the string will be added.
    string : str
        The string to be added.
    alignment : AlignmentOptions
        The alignment of the line.
    """
    if alignment == AlignmentOptions.LEFT:
        _add_str_left(window, line, string, attr)
    elif alignment == AlignmentOptions.CENTER:
        _add_str_centered(window, line, string, attr)
    elif alignment == AlignmentOptions.RIGHT:
        _add_str_right(window, line, string, attr)
    elif alignment == AlignmentOptions.MANUAL:
        window.addstr(line, col, string, attr)


def compute_strs_centered(window: curses.window, strings: list) -> list:
    """
    Compute the positions where a list of strings will be added to a window centered
    both horizontally and vertically.

    Parameters
    ----------
    window : curses.window
        The window where the strings will be added.
    strings : list
        The strings to be added.

    Returns
    -------
    list
        The positions where the strings will be added.
    """
    positions = []
    for i, string in enumerate(strings):
        positions.append(
            (
                (window.getmaxyx()[0] - len(strings)) // 2 + i,
                (window.getmaxyx()[1] - len(string)) // 2,
            )
        )
    return positions


def compute_strs_h_centered(
    window: curses.window,
    start_line: int,
    strings: list,
    orientation: OrientationOptions = OrientationOptions.VERTICAL,
) -> list[tuple]:
    """
    Compute the positions where a list of strings will be added to a window centered
    horizontally.

    Parameters
    ----------
    window : curses.window
        The window where the strings will be added.
    strings : list
        The strings to be added.

    Returns
    -------
    list[tuple]
        The coordinates (y,x) where the strings will be added.
    """
    positions = []
    if orientation == OrientationOptions.VERTICAL:
        for i, string in enumerate(strings):
            positions.append(
                (
                    start_line + i,
                    (window.getmaxyx()[1] - len(string)) // 2,
                )
            )
    else:
        sum_len = sum(len(string) for string in strings)
        spacing = (window.getmaxyx()[1] - sum_len) // (len(strings) + 1)
        next_start_x = spacing
        for string in strings:
            positions.append((start_line, next_start_x))
            next_start_x += len(string) + spacing
    return positions


def compute_strs_h_left(
    _window: curses.window,
    start_line: int,
    strings: list,
    orientation: OrientationOptions = OrientationOptions.VERTICAL,
) -> list[tuple]:
    positions = []
    next_start_x = 0
    for i, string in enumerate(strings):
        if orientation == OrientationOptions.VERTICAL:
            positions.append((start_line + i, 0))
        else:
            positions.append((start_line, next_start_x))
            next_start_x += len(string) + 1  # spacing = 1
    return positions


def compute_strs_h_right(
    window: curses.window,
    start_line: int,
    strings: list,
    orientation: OrientationOptions = OrientationOptions.VERTICAL,
) -> list[tuple]:
    positions = []
    if orientation == OrientationOptions.VERTICAL:
        for i, string in enumerate(strings):
            positions.append(
                (
                    start_line + i,
                    window.getmaxyx()[1] - len(string),
                )
            )
    else:
        spacing = 1
        sum_len = sum(len(string) for string in strings)
        next_start_x = window.getmaxyx()[1] - sum_len - spacing * (len(strings) - 1)
        for string in strings:
            positions.append((start_line, next_start_x))
            next_start_x += len(string) + spacing
    return positions


def compute_strs_h_aligned(
    window: curses.window,
    start_line: int,
    strings: list,
    orientation: OrientationOptions = OrientationOptions.VERTICAL,
    alignment: AlignmentOptions = AlignmentOptions.LEFT,
) -> list[tuple]:
    if alignment == AlignmentOptions.LEFT:
        return compute_strs_h_left(window, start_line, strings, orientation)
    elif alignment == AlignmentOptions.RIGHT:
        return compute_strs_h_right(window, start_line, strings, orientation)
    elif alignment == AlignmentOptions.CENTER:
        return compute_strs_h_centered(window, start_line, strings, orientation)
    return None
