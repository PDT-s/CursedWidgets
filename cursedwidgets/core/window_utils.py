import curses


def create_center_window(
    stdscr: curses.window, height: int, width: int
) -> curses.window:
    center_x, center_y = stdscr.getmaxyx()
    center_x = center_x // 2 - height // 2
    center_y = center_y // 2 - width // 2
    win = curses.newwin(height, width, center_x, center_y)
    win.box()
    return win


def compute_window_centered_position(
    stdscr: curses.window, height: int, width: int
) -> tuple[int, int]:
    """
    Compute the position where a window will be centered.

    Parameters
    ----------
    stdscr : curses.window
        The window where the new window will be centered.
    height : int
        Height of the new window.
    width : int
        Width of the new window.

    Returns
    -------
    tuple[int, int]
        The position (y, x) where the window will be centered.
    """
    center_y, center_x = stdscr.getmaxyx()
    center_x = center_x // 2 - width // 2
    center_y = center_y // 2 - height // 2
    return center_y, center_x
