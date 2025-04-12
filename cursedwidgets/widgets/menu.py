import curses

from .base import SelectableWidget
from cursedwidgets.constants import OrientationOptions, AlignmentOptions
from cursedwidgets.core.string_painter import compute_strs_h_aligned

class MenuSelector(SelectableWidget):
    def __init__(
        self,
        win: curses.window,
        options: list,
        y: int,
        x: int,
        height: int,
        width: int,
        orientation: OrientationOptions = OrientationOptions.VERTICAL,
        alignment: AlignmentOptions = AlignmentOptions.MANUAL,
    ):
        """
        Create a menu selector. The user can select an option from a list.
        It will be created a new window inside the given window to draw
        the selector.

        NOTE: If the orientation is VERTICAL and the options don't fit in the
        height of the sub-window, the user can scroll through the options with
        the arrow keys. Currently, there is no scroll implementation for
        HORIZONTAL orientation.

        Parameters
        ----------
        win : curses.window
            The window where the selector will be drawn.
        options : list
            The options that the user can select.
        y : int
            The y position of the top-left corner of the sub-window where the
            selector will be drawn. The position is relative to the window
            given.
        x : int
            The x position of the top-left corner of the sub-window where the
            selector will be drawn. The position is relative to the window
            given.
        height : int
            The height of the sub-window where the selector will be drawn.
        width : int
            The width of the sub-window where the selector will be drawn. If
            the orientation is VERTICAL, it should be at least
            max(len(option) for option in options) + 1 to take into account
            the null character at the end of the strings.
        orientation : OrientationOptions, optional
            Orientation of the options, by default OrientationOptions.VERTICAL
        alignment : AlignmentOptions, optional
            Alignment of the options, by default AlignmentOptions.MANUAL
        """
        self.win = win
        self.options = options
        self.y = y
        self.x = x
        self.height = height
        self.width = width
        self.orientation = orientation
        self.alignment = alignment
        self.first_option_idx = 0  # For scrolling in vertical orientation
        self.selected = 0
        self.subwin = None
        self._create_window()

    def _create_window(self) -> None:
        """
        Create the sub-window where the selector will be drawn.
        """
        max_w = self.win.getmaxyx()[1] - self.x
        self.width = min(self.width, max_w)
        self.subwin = self.win.derwin(self.height, self.width, self.y, self.x)
        self.subwin.keypad(True)

    def draw(self, is_active=False) -> None:
        """
        Draw the selector in the sub-window.

        Parameters
        ----------
        is_active : bool, optional
            True if this MenuSelector is active and False otherwise, by default False
        """
        if is_active:
            # Hide cursor if the selector is active
            curses.curs_set(0)
        # Clear the sub-window
        self.subwin.clear()
        # Take into account scroll for vertical orientation
        if self.orientation == OrientationOptions.VERTICAL:
            last_option_idx = min(
                self.first_option_idx + self.height - 1, len(self.options)
            )
            display_options = self.options[self.first_option_idx : last_option_idx + 1]
        else:
            display_options = self.options
        # Compute the coordinates where the options will be drawn depending on the
        # orientation and alignment
        option_coords = compute_strs_h_aligned(
            self.subwin, 0, display_options, self.orientation, self.alignment
        )
        # Draw the options in the sub-window in the computed coordinates
        for i, option in enumerate(display_options):
            y, x = option_coords[i]
            # Take into account scroll for vertical orientation
            if self.orientation == OrientationOptions.VERTICAL:
                i += self.first_option_idx
            if i == self.selected and is_active:
                # Highlight the selected option if the selector is active
                self.subwin.addstr(y, x, option, curses.A_REVERSE)
            else:
                self.subwin.addstr(y, x, option)
        # Refresh the sub-window
        self.subwin.refresh()

    def _handle_key_up(self):
        if self.orientation == OrientationOptions.VERTICAL and self.selected > 0:
            self.selected -= 1
            if self.selected < self.first_option_idx:
                self.first_option_idx = self.selected

    def _handle_key_down(self):
        max_idx = len(self.options) - 1
        if self.orientation == OrientationOptions.VERTICAL and self.selected < max_idx:
            self.selected += 1
            last_option_idx = min(
                self.first_option_idx + self.height - 1, len(self.options)
            )
            if self.selected > last_option_idx:
                self.first_option_idx += 1

    def handle_input(self, key: int) -> int:
        """
        Handle the input of the user. The user can move the selector with the
        arrow keys and select an option with the Enter key.

        Parameters
        ----------
        key : int
            The key that the user pressed.

        Returns
        -------
        int
            The index of the selected option if the user pressed Enter. None
            otherwise.
        """
        max_idx = len(self.options) - 1
        if key == curses.KEY_UP:
            self._handle_key_up()
        elif key == curses.KEY_DOWN:
            self._handle_key_down()
        elif (
            key == curses.KEY_LEFT
            and self.orientation == OrientationOptions.HORIZONTAL
            and self.selected > 0
        ):
            self.selected -= 1
        elif (
            key == curses.KEY_RIGHT
            and self.orientation == OrientationOptions.HORIZONTAL
            and self.selected < max_idx
        ):
            self.selected += 1
        elif key == ord("\n"):
            return self.selected
        return None

    def run(self) -> int:
        """
        Run the selector. The user can select an option from the list.

        Returns
        -------
        int
            The index of the selected option.
        """
        self.draw(is_active=True)
        while True:
            key = self.subwin.getch()
            result = self.handle_input(key)
            if result is not None:
                return result
            self.draw(is_active=True)

    def close(self):
        """
        Close the sub-window.
        """
        self.subwin.clear()
        self.subwin.refresh()
        del self.subwin