import curses

from .base import SelectableWidget
from ..utils import is_key_printable


class InputField(SelectableWidget):
    def __init__(
        self,
        win: curses.window,
        y: int,
        x: int,
        label: str,
        is_password: bool = False,
        max_length: int = 15,
        spacing: int = 1,
    ) -> None:
        """
        Create an input field. The user can input text. It will be created a
        new window inside the given window to draw the input field.

        Parameters
        ----------
        win : curses.window
            The window where the input field will be drawn.
        y : int
            The y position of the top-left corner of the sub-window where the
            input field will be drawn. The position is relative to the window
            given.
        x : int
            The x position of the top-left corner of the sub-window where the
            input field will be drawn. The position is relative to the window
            given.
        label : str
            The label of the input field. Displayed at the left of the input
            field.
        is_password : bool, optional
            True if the input field is a password and the text showed should
            be hidden and False otherwise, by default False
        max_length : int, optional
            Maximum length of the input field, by default 15
        spacing : int, optional
            Spacing between the label and the input field, by default 1
        """
        self.win = win
        self.y = y
        self.x = x
        self.label = label
        self.is_password = is_password
        self.max_length = max_length
        self.spacing = spacing
        self.text = ""  # value showed to the user
        self._value = ""  # true value
        self.subwin = None
        self._create_window()

    def _create_window(self) -> None:
        """
        Create the sub-window where the input field will be drawn.
        """
        # When calculating the width of the sub-window, we need to consider the null character
        # at the end of the string
        win_width = min(
            self.max_length + len(self.label) + self.spacing + 1, self.win.getmaxyx()[1]
        )
        self.max_length = (
            win_width - len(self.label) - self.spacing - 1
        )  # Adjust max_length
        if self.max_length < 0:
            self.max_length = 0
        self.subwin = self.win.derwin(1, win_width, self.y, self.x)

    def draw(self, is_active=False) -> None:
        """
        Draw the input field in the sub-window.

        Parameters
        ----------
        is_active : bool, optional
            True if this input field is active and False otherwise,
            by default False
        """
        # Clear the sub-window
        self.subwin.clear()
        # Draw the label in bold and then the text
        self.subwin.addstr(0, 0, self.label, curses.A_BOLD)
        self.subwin.addstr(0, len(self.label) + 1, self.text)
        if is_active:
            # Make the cursor visible and make it blink
            curses.curs_set(2)
            # Relative coordinates within self.win
            cursor_y = self.y
            cursor_x = self.x + len(self.label) + 1 + len(self.text)
            # Ensure the coordinates are within self.win
            cursor_x = max(0, min(cursor_x, self.x + self.subwin.getmaxyx()[1] - 1))
            # Move the cursor at the end of the text
            self.win.move(cursor_y, cursor_x)
        # Refresh the sub-window
        self.subwin.refresh()

    def handle_input(self, key: int) -> None:
        """
        Handle the input of the user. The user can input text and delete it
        with the backspace key.

        Parameters
        ----------
        key : int
            The key that the user pressed.
        """
        if is_key_printable(key) and len(self.text) < self.max_length:
            self.text += chr(key) if not self.is_password else "*"
            self._value += chr(key)
        elif key == curses.KEY_BACKSPACE:
            self.text = self.text[:-1]
            self._value = self._value[:-1]
        return None

    def get_value(self) -> str:
        """
        Get the value of the input field.

        Returns
        -------
        str
            The value of the input field.
        """
        return self._value

    def close(self):
        """
        Close the sub-window and clean up.
        """
        self.subwin.clear()
        self.subwin.refresh()
        del self.subwin
