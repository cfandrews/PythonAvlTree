# Copyright 2023 Charles Andrews
"""Contains the AvlTreeNode class."""
from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic, TypeVar

from ._avl_tree_element import AvlTreeElement

if TYPE_CHECKING:  # pragma: no cover
    from uuid import UUID

_T = TypeVar("_T", bound=AvlTreeElement)


class AvlTreeNode(Generic[_T]):
    """Represents a single node in an AvlTree.

    In order to prevent AvlTree objects and method calls from becoming highly recursive,
    instances of this class do not contain direct references to their children and do
    not handle any tree logic. Instead, instances of this class contain identifiers
    which can be mapped to their children by the containing AvlTree instance.
    """

    def __init__(self, element: _T) -> None:
        """Constructor.

        Args:
            element (_T): The element contained in this node.
        """
        self.__element: Final[_T] = element
        self.__lesser_child_identifier: UUID | None = None
        self.__greater_child_identifier: UUID | None = None

    @property
    def element(self) -> _T:
        """Gets the element contained in this node.

        Returns:
            _T: The element contained in this node.
        """
        return self.__element

    @property
    def lesser_child_identifier(self) -> UUID | None:
        """Gets the identifier of the lesser child of this node.

        Returns:
            UUID | None: The identifier of the lesser child of this node.
        """
        return self.__lesser_child_identifier

    @lesser_child_identifier.setter
    def lesser_child_identifier(self, lesser_child_identifier: UUID | None) -> None:
        """Sets the identifier of the lesser child of this node.

        Args:
            lesser_child_identifier (UUID | None): The identifier of the lesser child of
                this node.
        """
        self.__lesser_child_identifier = lesser_child_identifier

    @property
    def greater_child_identifier(self) -> UUID | None:
        """Gets the identifier of the greater child of this node.

        Returns:
            UUID | None: The identifier of the greater child of this node.
        """
        return self.__greater_child_identifier

    @greater_child_identifier.setter
    def greater_child_identifier(self, greater_child_identifier: UUID | None) -> None:
        """Sets the identifier of the greater child of this node.

        Args:
            greater_child_identifier (UUID | None): The identifier of the greater child
                of this node.
        """
        self.__greater_child_identifier = greater_child_identifier
