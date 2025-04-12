import curses

from cursedwidgets.widgets.base import SelectableWidget


class WidgetManager:
    def __init__(self, widgets: list[SelectableWidget]):
        """
        Create a menu manager. The user can switch between widgets using the
        Tab key.

        Parameters
        ----------
        widgets : list[SelectableComponent]
            The widgets that the user can switch between.
        """
        self.widgets = widgets
        self.active_selector = 0

    def draw_all(self):
        """
        Draw all the widgets.
        """
        for i, selector in enumerate(self.widgets):
            selector.draw(is_active=(i == self.active_selector))

    def run(self, stdscr: curses.window) -> tuple[int, int]:
        """
        Run the menu manager. The user can switch between widgets using the
        Tab key and select an option from the active selector.

        Parameters
        ----------
        stdscr : curses.window
            The standard screen where the widgets will be drawn.

        Returns
        -------
        tuple[int, int]
            The index of the active selector and the index of the selected option
            from the active selector.
        """
        self.draw_all()
        while True:
            key = stdscr.getch()
            if key == ord("\t"):  # Tab for switching between widgets
                self.active_selector = (self.active_selector + 1) % len(self.widgets)
            else:
                result = self.widgets[self.active_selector].handle_input(key)
                if result is not None:
                    return (
                        self.active_selector,
                        result,
                    )  # Returns (selector_idx, option_idx)
            self.draw_all()