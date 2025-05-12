import sys
import curses

from cursedwidgets.widgets import InputField
from cursedwidgets.widgets.base import SelectableWidget
from cursedwidgets.core import window_utils, string_painter
from cursedwidgets.constants import AlignmentOptions


def _draw_all(widgets: list[SelectableWidget], active_idx: int):
    for i, field in enumerate(widgets):
        field: SelectableWidget
        field.draw(is_active=(active_idx == i))


def _draw_input_values(input_fields: list[InputField], start_row: int):
    win: curses.window = input_fields[0].win
    for i, input_field in enumerate(input_fields):
        content = f"{input_field.label} content: " + input_field.get_value()
        win.addstr(start_row + 2 * i, 2, content)


def main(stdscr: curses.window):
    stdscr.clear()

    win = window_utils.create_center_window(stdscr, height=20, width=60)
    win.box()
    win.keypad(True)
    win.refresh()

    # Define the content we are going to print

    title = "INPUT DEMO"

    tips = [
        "Type CTRL-C to Exit",
        "Type TAB to switch between input fields",
        "Type ENTER to show input values",
    ]

    first_input_row = len(tips) + 8
    input_fields: list[SelectableWidget] = []
    input_fields.append(
        InputField(win, first_input_row, 3, "Input example:", is_password=False)
    )
    input_fields.append(
        InputField(win, first_input_row + 2, 3, "Password example:", is_password=True)
    )

    # Print the title
    string_painter.add_str_align(win, 1, 1, title, AlignmentOptions.CENTER)

    # Print the tips
    row = 3  # row for the first tip
    for i, tip in enumerate(tips):
        win.addstr(row, 2, f"{i + 1}. {tip}")
        row += 1
    win.refresh()

    # Print input values and labels
    _draw_input_values(input_fields, row + 1)

    # Print input fields
    active_field_idx = 0
    _draw_all(input_fields, active_field_idx)

    while True:
        key = win.getch()
        if key == ord("\t"):
            active_field_idx += 1
            active_field_idx %= len(input_fields)
        elif key == ord("\n"):
            _draw_input_values(input_fields, row + 1)
        else:
            input_fields[active_field_idx].handle_input(key)
        _draw_all(input_fields, active_field_idx)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
