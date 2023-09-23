# Copyright 2023 Charles Andrews
"""Contains the AvlTree class."""
from __future__ import annotations

from typing import TYPE_CHECKING, Final, Iterator, MutableSet, TypeVar
from uuid import uuid4

from ._avl_tree_element import AvlTreeElement
from ._avl_tree_node import AvlTreeNode

if TYPE_CHECKING:  # pragma: no cover
    from uuid import UUID

_T = TypeVar("_T", bound=AvlTreeElement)


class AvlTree(MutableSet[_T]):
    """Lightweight, pure-python AVL tree.

    This class implements the MutableSet interface.
    """

    def __init__(self) -> None:
        """Constructor."""
        self.__nodes: Final[dict[UUID, AvlTreeNode[_T]]] = {}
        self.__root_identifier: UUID | None = None

    def add(self, value: _T) -> None:
        """Adds the given value to this tree.

        Args:
            value (_T): The value to add to this tree.
        """
        if self.__root_identifier is None:
            self.__root_identifier = uuid4()
            self.__nodes[self.__root_identifier] = AvlTreeNode[_T](element=value)
            return
        identifier: Final[UUID] = uuid4()
        node: Final[AvlTreeNode[_T]] = AvlTreeNode[_T](element=value)
        current_node: AvlTreeNode[_T] = self.__nodes[self.__root_identifier]
        while current_node.element != value:
            if (
                value < current_node.element
                and current_node.lesser_child_identifier is None
            ):
                current_node.lesser_child_identifier = identifier
                self.__nodes[identifier] = node
            elif (
                current_node.element < value
                and current_node.greater_child_identifier is None
            ):
                current_node.greater_child_identifier = identifier
                self.__nodes[identifier] = node
            elif (
                value < current_node.element
                and current_node.lesser_child_identifier is not None
            ):
                current_node = self.__nodes[current_node.lesser_child_identifier]
            elif current_node.greater_child_identifier is not None:
                current_node = self.__nodes[current_node.greater_child_identifier]

    def discard(self, value: _T) -> None:  # noqa: C901, PLR0912
        """Removes the given value from this tree in an idempotent way.

        Args:
            value (_T): The value to remove from this tree.
        """
        if self.__root_identifier is None:
            return

        # Find the node to discard and its parent node
        parent: AvlTreeNode[_T] | None = None
        node_identifier: UUID = self.__root_identifier
        node: AvlTreeNode[_T] = self.__nodes[node_identifier]
        while node.element != value:
            parent = node
            if value < node.element and node.lesser_child_identifier is not None:
                node_identifier = node.lesser_child_identifier
                node = self.__nodes[node_identifier]
            elif node.element < value and node.greater_child_identifier is not None:
                node_identifier = node.greater_child_identifier
                node = self.__nodes[node_identifier]
            else:
                return

        # Find the identifier of the node with which to replace the existing node
        replacement_identifier: UUID | None = None
        if (
            node.lesser_child_identifier is not None
            and node.greater_child_identifier is None
        ):
            replacement_identifier = node.lesser_child_identifier
        elif (
            node.lesser_child_identifier is None
            and node.greater_child_identifier is not None
        ):
            replacement_identifier = node.greater_child_identifier
        elif (
            node.lesser_child_identifier is not None
            and node.greater_child_identifier is not None
        ):
            # Find the next highest node than the one to remove
            successor_parent: AvlTreeNode[_T] | None = None
            replacement_identifier = node.greater_child_identifier
            successor: AvlTreeNode[_T] = self.__nodes[replacement_identifier]
            while successor.lesser_child_identifier is not None:
                successor_parent = successor
                replacement_identifier = successor.lesser_child_identifier
                successor = self.__nodes[successor.lesser_child_identifier]

            # Swap the successor node with the node to replace
            if (
                successor_parent is not None
                and successor.greater_child_identifier is None
            ):
                successor_parent.lesser_child_identifier = None
                successor.greater_child_identifier = node.greater_child_identifier
            elif successor_parent is not None:
                successor_parent.lesser_child_identifier = (
                    successor.greater_child_identifier
                )
                successor.greater_child_identifier = node.greater_child_identifier
            successor.lesser_child_identifier = node.lesser_child_identifier

        # Swap the node to its replacement
        if parent is None:
            self.__root_identifier = replacement_identifier
        elif parent.lesser_child_identifier == node_identifier:
            parent.lesser_child_identifier = replacement_identifier
        else:
            parent.greater_child_identifier = replacement_identifier
        del self.__nodes[node_identifier]

    def __contains__(self, x: object) -> bool:
        """Determines whether the given object is an element of this tree.

        Args:
            x (object): The object to check for membership.

        Returns:
            bool: Whether the given object is an element of this tree.
        """
        if self.__root_identifier is None:
            return False
        current_node: AvlTreeNode[_T] = self.__nodes[self.__root_identifier]
        while current_node.element != x:
            if not isinstance(x, current_node.element.__class__):
                return False
            if (
                not current_node.element < x
                and current_node.lesser_child_identifier is not None
            ):
                current_node = self.__nodes[current_node.lesser_child_identifier]
            elif (
                current_node.element < x
                and current_node.greater_child_identifier is not None
            ):
                current_node = self.__nodes[current_node.greater_child_identifier]
            else:
                return False
        return True

    def __len__(self) -> int:
        """Returns the number of elements contained in this tree.

        Returns:
            int: The number of elements contained in this tree.
        """
        return len(self.__nodes)

    def __iter__(self) -> Iterator[_T]:
        """Iterates over all elements contained in this tree in sort order.

        Returns:
            Iterator[_T]: The iterator object.
        """
        if self.__root_identifier is not None:
            stack: Final[list[UUID]] = [self.__root_identifier]
            yielded: Final[set[UUID]] = set()
            while len(stack) > 0:
                identifier = stack.pop(-1)
                node = self.__nodes[identifier]
                if (
                    node.lesser_child_identifier is None
                    and node.greater_child_identifier is None
                ):
                    yielded.add(identifier)
                    yield node.element
                elif (
                    node.lesser_child_identifier is not None
                    and node.lesser_child_identifier not in yielded
                ):
                    stack.append(identifier)
                    stack.append(node.lesser_child_identifier)
                elif node.greater_child_identifier is not None:
                    stack.append(node.greater_child_identifier)
                    yielded.add(identifier)
                    yield node.element
                else:
                    yielded.add(identifier)
                    yield node.element

    def minimum(self) -> _T | None:
        """Gets the minimum element contained in this tree.

        Returns:
            _T | None: The minimum element contained in this tree.
        """
        if self.__root_identifier is None:
            return None
        node: AvlTreeNode[_T] = self.__nodes[self.__root_identifier]
        while node.lesser_child_identifier is not None:
            node = self.__nodes[node.lesser_child_identifier]
        return node.element
