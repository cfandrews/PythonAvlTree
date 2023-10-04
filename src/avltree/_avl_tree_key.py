# Copyright 2023 Charles Andrews
"""Contains the AvlTreeKey class."""
from abc import abstractmethod
from typing import Any, Protocol


class AvlTreeKey(Protocol):
    """Protocol which defines a key which can be stored in an AvlTree."""

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Determines whether this object compares equal to another.

        Args:
            other (object): The other object to compare against.

        Returns:
            bool: Whether this object compares equal to the other.
        """

    @abstractmethod
    def __hash__(self) -> int:
        """Returns the hash of this object.

        Returns:
            int: The hash of this object.
        """

    @abstractmethod
    def __lt__(self, other: Any) -> bool:  # noqa: ANN401
        """Determines whether this object compares less than another.

        Args:
            other (Any): The other object to compare against.

        Returns:
            bool: Whether this object compares less than the other.
        """
