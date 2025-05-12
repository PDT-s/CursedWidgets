import curses
from ..utils import is_key_printable
from ..constants import SPECIAL_KEYS
from .base import SelectableWidget


class TextBox(SelectableWidget):
    def __init__(
        self,
        win: curses.window,
        y: int,
        x: int,
        height: int,
        width: int,
        text: str,
        edit_key: str = None,
    ):
        self.win = win
        self.y = y
        self.x = x
        self.height = height
        self.width = width
        self.box_height = height - 2
        self.box_width = width - 2
        self.lines = self._split_text(text)
        self.edit_key = edit_key
        self.cursor_x = 1  # Cursor x position relative to the sub-window
        self.cursor_y = 1  # Cursor y position relative to the sub-window
        self.first_line_idx = 0
        self._edited = False  # Flag to indicate if the text was edited
        self._editable = edit_key is None  # Flag to indicate if the text is editable
        self._create_window()
        self._register_key_callbacks()
        self._add_text()

    def _create_window(self) -> None:
        """
        Create the sub-window where the editable box will be drawn.
        """
        max_w = self.win.getmaxyx()[1] - self.x
        self.width = min(self.width, max_w)
        self.subwin = self.win.derwin(self.height, self.width, self.y, self.x)
        self.subwin.keypad(True)

    def _split_text(self, text: str) -> list:
        """
        Split the text into lines of length `self.width`.

        Parameters
        ----------
        text : str
            The text to be split.

        Returns
        -------
        list
            A list of strings, each string representing a line of the text.
        """
        n_lines = (len(text) + self.box_width + 1) // self.box_width
        lines = []
        for i in range(n_lines):
            lines.append(text[i * self.box_width : (i + 1) * self.box_width])
        if lines == []:
            lines = [""]
        return lines

    def _add_text(self) -> None:
        """
        Add the text to the window. This method is called when the
        window is drawn.
        """
        i = self.first_line_idx
        n = 0
        while i < len(self.lines) and n < self.box_height:
            self.subwin.addstr(n + 1, 1, self.lines[i])
            i += 1
            n += 1

    def _move(self):
        """
        Move the cursor to the current position.
        """
        h, w = self.subwin.getmaxyx()
        self.cursor_y = max(
            1, min(self.cursor_y, h - 2)
        )  # Take into account the border
        self.cursor_x = max(
            1, min(self.cursor_x, w - 2)
        )  # Take into account the border
        self.win.move(self.y + self.cursor_y, self.x + self.cursor_x)

    def draw(self, is_active: bool = False) -> None:
        """
        Draw the editable box in the sub-window.

        Parameters
        ----------
        is_active : bool, optional
            True if this EditableBox is active and False otherwise, by default False
        """
        # if self._edited:
        self.subwin.clear()
        self.subwin.box()
        self._add_text()
        # self._edited = False

        if is_active:
            # Show the cursor if the EditableBox is active and make it blink
            curses.curs_set(2)
            self._move()
        self.subwin.refresh()

    def _recompute_lines(self):
        """
        Recompute the lines of the text. This method is called
        after an edit is made to the text.
        """
        text = "".join(self.lines)
        self.lines = self._split_text(text)

    def _is_last_line(self) -> bool:
        """
        Returns True if the cursor is at the last line of the text
        and False otherwise.

        Returns
        -------
        bool
            True if the cursor is at the last line of the text and False otherwise.
        """
        return self.first_line_idx + self.cursor_y == len(self.lines)

    def _key_up_callback(self) -> None:
        """
        Move the cursor up.
        """
        if self.cursor_y == 1 and self.first_line_idx > 0:
            # Scroll up if the cursor is at the top of the window
            # and it is not the first line of the text
            self.first_line_idx -= 1
            self._edited = True
        self.cursor_y = max(1, self.cursor_y - 1)

    def _key_down_callback(self) -> None:
        """
        Move the cursor down.
        """
        if len(self.lines) == 1:
            return
        # Avoid moving the cursor down where there is no text
        is_last_line_minus_one = (
            self.first_line_idx + self.cursor_y == len(self.lines) - 1
        )
        if is_last_line_minus_one and self.cursor_x - 1 > len(self.lines[-1]):
            return

        if self.cursor_y == self.box_height and not self._is_last_line():
            # Scroll down if the cursor is at the bottom of the window
            # and it is not the last line of the text
            self.first_line_idx += 1
            self._edited = True
        self.cursor_y = min(self.box_height, self.cursor_y + 1)

    def _key_left_callback(self) -> None:
        """
        Move the cursor to the left.
        """
        # Avoid moving the cursor to the left if it is at the beginning of the text
        if self.cursor_x == 1 and self.cursor_y == 1 and self.first_line_idx == 0:
            return

        if self.cursor_x == 1 and self.cursor_y == 1:
            # Scroll up if the cursor is at the top of the window
            self.first_line_idx -= 1
            self._edited = True
            self.cursor_x = self.box_width
        elif self.cursor_x == 1:
            # Move the cursor to the end of the previous line
            self.cursor_x = self.box_width
            self.cursor_y -= 1
        else:
            # Move the cursor to the left
            self.cursor_x -= 1

    def _key_right_callback(self) -> None:
        """
        Move the cursor to the right.
        """
        # Avoid moving the cursor to the right if it is at the end of the text
        if self._is_last_line() and self.cursor_x - 1 == len(self.lines[-1]):
            return
        if self.cursor_x == self.box_width and self.cursor_y == self.box_height:
            # Scroll down if the cursor is at the bottom of the window
            self.first_line_idx += 1
            self._edited = True
            self.cursor_x = 1
        elif self.cursor_x == self.box_width:
            # Move the cursor to the beginning of the next line
            self.cursor_x = 1
            self.cursor_y += 1
        else:
            # Move the cursor to the right
            self.cursor_x += 1

    def _key_esc_callback(self) -> None:
        """
        Turn off the editable flag.
        """
        if self.edit_key is not None:
            self._editable = False

    def _check_editable_flag(self, char: str) -> bool:
        """
        Returns True if `_editable` flag is on and False
        otherwise. If `char` is the `edit_key`, the `_editable`
        flag is turned on.

        Parameters
        ----------
        char : str
            Char entered by the user

        Returns
        -------
        bool
            True if `_editable` flag is on and False otherwise
        """
        if not self._editable:
            self._editable = self.edit_key == char
            return False
        return True

    def _add_char(self, char: str) -> None:
        """
        Add a character to the text.

        Parameters
        ----------
        char : str
            The character to be added.
        """
        # Check if the text is editable
        if not self._check_editable_flag(char):
            return
        # Place the character in the correct line
        line_idx = self.first_line_idx + self.cursor_y - 1
        line = self.lines[line_idx]
        line = line[: self.cursor_x - 1] + char + line[self.cursor_x - 1 :]
        self.lines[line_idx] = line
        # Move the cursor taking into account the borders
        if self.cursor_x < self.box_width:
            # Move the cursor to the right
            self.cursor_x += 1
        elif self.cursor_y < self.box_height:
            # Move the cursor to the beginning of the next line
            self.cursor_x = 1
            self.cursor_y += 1
        else:
            # Scroll down if the cursor is at the bottom of the window
            self.first_line_idx += 1
            self.cursor_x = 1
        # Recompute the lines
        self._recompute_lines()
        # Turn on the _edited flag
        self._edited = True

    def _remove_char(self) -> None:
        """
        Remove a character from the text.
        """
        # Check if the text is editable
        if not self._editable:
            return
        # Avoid removing a character if the cursor is at the beginning of the text
        if self.cursor_x == 1 and self.cursor_y == 1:
            return

        if self.cursor_x > 1:
            # Remove the character in the correct line
            line_idx = self.first_line_idx + self.cursor_y - 1
            line = self.lines[line_idx]
            line = line[: self.cursor_x - 2] + line[self.cursor_x - 1 :]
            self.lines[line_idx] = line
            # Move the cursor
            self.cursor_x -= 1
        elif self.cursor_x == 1:
            # Remove the character in the correct line
            line_idx = self.first_line_idx + self.cursor_y - 2
            line = self.lines[line_idx]  # Previous line
            line = line[:-1]
            self.lines[line_idx] = line
            # Move the cursor
            self.cursor_x = self.width
            self.cursor_y -= 1
        # Recompute the lines
        self._recompute_lines()
        # Turn on the _edited flag
        self._edited = True

    def _register_key_callbacks(self):
        """
        Register the key callbacks.
        """
        self.key_callbacks = {
            curses.KEY_UP: self._key_up_callback,
            curses.KEY_DOWN: self._key_down_callback,
            curses.KEY_LEFT: self._key_left_callback,
            curses.KEY_RIGHT: self._key_right_callback,
            curses.KEY_BACKSPACE: self._remove_char,
            SPECIAL_KEYS.ESCAPE: self._key_esc_callback,
        }

    def handle_input(self, key: int) -> None:
        """
        Execute the key callback associated with the key.

        Parameters
        ----------
        key : int
            The key to be processed
        """
        if key in self.key_callbacks:
            self.key_callbacks[key]()
        elif is_key_printable(key):
            self._add_char(chr(key))
        return None

    def get_text(self) -> str:
        """
        Get the text entered by the user.

        Returns
        -------
        str
            The text entered by the user.
        """
        return "".join(self.lines)

    def close(self) -> None:
        """
        Close the sub-window.
        """
        self.subwin.clear()
        self.subwin.refresh()
        del self.subwin