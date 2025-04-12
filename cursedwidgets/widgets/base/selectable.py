from abc import ABC, abstractmethod


class SelectableWidget(ABC):
    @abstractmethod
    def draw(self, is_active: bool) -> None:
        """
        Draws the component.
        Parameters
        ----------
        is_active : bool
            Indicates whether the component is active.
        """

        pass

    @abstractmethod
    def handle_input(self, key: str) -> int:
        """
        Handles the input key and performs the corresponding action.
        Parameters
        ----------
        key : str
            The input key to handle.
        Returns
        -------
        int
            An integer indicating the result of handling the input.
        """

        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closes the selectable component.
        This method should be overridden by subclasses to implement
        specific closing behavior for the component.
        """
        pass
