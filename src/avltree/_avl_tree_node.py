# Copyright 2023 Charles Andrews
"""Contains the AvlTreeNode class."""
from __future__ import annotations

from typing import Generic, TypeVar

from ._avl_tree_key import AvlTreeKey

_K = TypeVar("_K", bound=AvlTreeKey)
_V = TypeVar("_V", bound=object)


class AvlTreeNode(Generic[_K, _V]):
    """Represents a single node in an AvlTree.

    In order to prevent AvlTree objects and method calls from becoming highly recursive,
    instances of this class do not contain direct references to their children and do
    not handle any tree logic. Instead, instances of this class contain keys which can
    be mapped to their children by the containing AvlTree instance.
    """

    def __init__(self, value: _V) -> None:
        """Constructor.

        Args:
            value (_V): The value contained in this node.
        """
        self.__value: _V = value
        self.__lesser_child_key: _K | None = None
        self.__greater_child_key: _K | None = None
        self.__height: int = 0

    @property
    def value(self) -> _V:
        """Gets the value contained in this node.

        Returns:
            _V: The value contained in this node.
        """
        return self.__value

    @value.setter
    def value(self, value: _V) -> None:
        """Sets the value contained in this node.

        Args:
            value (_V): The value contained in this node.
        """
        self.__value = value

    @property
    def lesser_child_key(self) -> _K | None:
        """Gets the key of the lesser child of this node.

        Returns:
            _K | None: The key of the lesser child of this node.
        """
        return self.__lesser_child_key

    @lesser_child_key.setter
    def lesser_child_key(self, lesser_child_key: _K | None) -> None:
        """Sets the key of the lesser child of this node.

        Args:
            lesser_child_key (_K | None): The key of the lesser child of this node.
        """
        self.__lesser_child_key = lesser_child_key

    @property
    def greater_child_key(self) -> _K | None:
        """Gets the key of the greater child of this node.

        Returns:
            _K | None: The key of the greater child of this node.
        """
        return self.__greater_child_key

    @greater_child_key.setter
    def greater_child_key(self, greater_child_key: _K | None) -> None:
        """Sets the key of the greater child of this node.

        Args:
            greater_child_key (_K | None): The key of the greater child of this node.
        """
        self.__greater_child_key = greater_child_key

    @property
    def height(self) -> int:
        """Gets the height of this node.

        Returns:
            int: The height of this node.
        """
        return self.__height

    @height.setter
    def height(self, height: int) -> None:
        """Sets the height of this node.

        Args:
            height (int): The height of this node.
        """
        self.__height = height
