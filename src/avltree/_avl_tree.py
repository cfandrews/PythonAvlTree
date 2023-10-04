# Copyright 2023 Charles Andrews
"""Contains the AvlTree class."""
from __future__ import annotations

from typing import Final, Iterator, MutableMapping, TypeVar

from ._avl_tree_key import AvlTreeKey
from ._avl_tree_node import AvlTreeNode

_K = TypeVar("_K", bound=AvlTreeKey)
_V = TypeVar("_V", bound=object)


class AvlTree(MutableMapping[_K, _V]):
    """Lightweight, pure-python AVL tree.

    This class implements the MutableMapping interface.
    """

    def __init__(self) -> None:
        """Constructor."""
        self.__nodes: Final[dict[_K, AvlTreeNode[_K, _V]]] = {}
        self.__root_key: _K | None = None

    def __setitem__(self, __k: _K, __v: _V) -> None:
        """Maps the given key to the given value in this tree.

        Args:
            __k (_K): The key to map.
            __v (_V): The value to associate with the key.
        """
        if __k in self.__nodes:
            self.__nodes[__k].value = __v
            return
        if self.__root_key is None:
            self.__root_key = __k
            self.__nodes[self.__root_key] = AvlTreeNode[_K, _V](value=__v)
            return
        current_key: _K = self.__root_key
        current_node: AvlTreeNode[_K, _V] = self.__nodes[current_key]
        while True:
            if __k < current_key and current_node.lesser_child_key is None:
                current_node.lesser_child_key = __k
                self.__nodes[__k] = AvlTreeNode[_K, _V](value=__v)
                return
            if current_key < __k and current_node.greater_child_key is None:
                current_node.greater_child_key = __k
                self.__nodes[__k] = AvlTreeNode[_K, _V](value=__v)
                return
            if __k < current_key and current_node.lesser_child_key is not None:
                current_key = current_node.lesser_child_key
                current_node = self.__nodes[current_node.lesser_child_key]
            elif current_node.greater_child_key is not None:
                current_key = current_node.greater_child_key
                current_node = self.__nodes[current_node.greater_child_key]

    def __delitem__(self, __k: _K) -> None:  # noqa: C901
        """Deletes the given key from this tree.

        Args:
            __k (_K): The key to delete from this tree.

        Raises:
            KeyError: If the given key is not present in this tree.
        """
        if self.__root_key is None:
            message: str = f"Key not present in AvlTree: {__k!r}"
            raise KeyError(message)

        # Find the node to discard and its parent node
        parent: AvlTreeNode[_K, _V] | None = None
        node_key: _K = self.__root_key
        node: AvlTreeNode[_K, _V] = self.__nodes[node_key]
        while node_key != __k:
            parent = node
            node_key = self.__get_closer_key(key=__k, current_key=node_key)
            node = self.__nodes[node_key]

        # Find the key of the node with which to replace the existing node
        replacement_key: _K | None = None
        if node.lesser_child_key is not None and node.greater_child_key is None:
            replacement_key = node.lesser_child_key
        elif node.lesser_child_key is None and node.greater_child_key is not None:
            replacement_key = node.greater_child_key
        elif node.lesser_child_key is not None and node.greater_child_key is not None:
            # Find the next highest node than the one to remove
            successor_parent: AvlTreeNode[_K, _V] | None = None
            replacement_key = node.greater_child_key
            successor: AvlTreeNode[_K, _V] = self.__nodes[replacement_key]
            while successor.lesser_child_key is not None:
                successor_parent = successor
                replacement_key = successor.lesser_child_key
                successor = self.__nodes[successor.lesser_child_key]

            # Swap the successor node with the node to replace
            if successor_parent is not None and successor.greater_child_key is None:
                successor_parent.lesser_child_key = None
                successor.greater_child_key = node.greater_child_key
            elif successor_parent is not None:
                successor_parent.lesser_child_key = successor.greater_child_key
                successor.greater_child_key = node.greater_child_key
            successor.lesser_child_key = node.lesser_child_key

        # Swap the node to its replacement
        if parent is None:
            self.__root_key = replacement_key
        elif parent.lesser_child_key == node_key:
            parent.lesser_child_key = replacement_key
        else:
            parent.greater_child_key = replacement_key
        del self.__nodes[node_key]

    def __getitem__(self, __k: _K) -> _V:
        """Gets the value associated with the given key.

        Args:
            __k (_K): The key.

        Returns:
            _V: The value associated with the given key.

        Raises:
            KeyError: If the given key is not present in this tree.
        """
        if self.__root_key is None:
            message: str = f"Key not present in AvlTree: {__k!r}"
            raise KeyError(message)
        current_key: _K = self.__root_key
        current_node: AvlTreeNode[_K, _V] = self.__nodes[current_key]
        while current_key != __k:
            current_key = self.__get_closer_key(key=__k, current_key=current_key)
            current_node = self.__nodes[current_key]
        return current_node.value

    def __len__(self) -> int:
        """Returns the number of items contained in this tree.

        Returns:
            int: The number of items contained in this tree.
        """
        return len(self.__nodes)

    def __iter__(self) -> Iterator[_K]:
        """Iterates over all keys contained in this tree in sort order.

        Returns:
            Iterator[_K]: The iterator object.
        """
        if self.__root_key is None:
            return
        stack: Final[list[tuple[_K, bool]]] = [(self.__root_key, False)]
        while len(stack) > 0:
            key, lesser_child_visited = stack.pop(-1)
            node: AvlTreeNode[_K, _V] = self.__nodes[key]
            if node.lesser_child_key is not None and not lesser_child_visited:
                stack.append((key, True))
                stack.append((node.lesser_child_key, False))
            elif node.greater_child_key is not None:
                stack.append((node.greater_child_key, False))
                yield key
            else:
                yield key

    def minimum(self) -> _K:
        """Gets the minimum key contained in this tree.

        Returns:
            _K: The minimum key.

        Raises:
            ValueError: If there are no keys present in this tree.
        """
        if self.__root_key is None:
            message: Final[str] = "Cannot get the minimum of an empty AvlTree"
            raise ValueError(message)
        key: _K = self.__root_key
        while self.__nodes[key].lesser_child_key is not None:
            key = self.__nodes[key].lesser_child_key  # type: ignore[assignment]
        return key

    def maximum(self) -> _K:
        """Gets the maximum key contained in this tree.

        Returns:
            _K: The maximum key.

        Raises:
            ValueError: If there are no keys present in this tree.
        """
        if self.__root_key is None:
            message: Final[str] = "Cannot get the maximum of an empty AvlTree"
            raise ValueError(message)
        key: _K = self.__root_key
        while self.__nodes[key].greater_child_key is not None:
            key = self.__nodes[key].greater_child_key  # type: ignore[assignment]
        return key

    def __get_closer_key(self, key: _K, current_key: _K) -> _K:
        """Gets the next closest key to the given key.

        Args:
            key (_K): The key to search for.
            current_key (_K): The current key.

        Returns:
            _K: The next closest key to the given key.

        Raises:
            KeyError: If the given key is not present in this tree.
        """
        current_node: Final[AvlTreeNode[_K, _V]] = self.__nodes[current_key]
        if key < current_key and current_node.lesser_child_key is not None:
            return current_node.lesser_child_key
        if current_key < key and current_node.greater_child_key is not None:
            return current_node.greater_child_key
        message: Final[str] = f"Key not present in AvlTree: {key!r}"
        raise KeyError(message)
