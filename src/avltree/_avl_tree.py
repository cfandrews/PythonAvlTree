# Copyright 2023 Charles Andrews
"""Contains the AvlTree class."""
from __future__ import annotations

from typing import Final, Iterator, Literal, Mapping, MutableMapping, TypeVar, cast

from ._avl_tree_key import AvlTreeKey
from ._avl_tree_node import AvlTreeNode

_K = TypeVar("_K", bound=AvlTreeKey)
_V = TypeVar("_V", bound=object)


class AvlTree(MutableMapping[_K, _V]):
    """Lightweight, pure-python AVL tree.

    This class implements the MutableMapping interface and can be used in almost every
    way that a built-in dictionary can.

    # Sorting
    The AVL tree data structure makes it possible to easily iterate on keys in
    sort-order, and any method which returns an iterable of keys, values, or items will
    return them in sort-order by key.

    # Keys
    Anything used as a key in an AvlTree must implement `__eq__`, `__hash__`, and
    `__lt__`. That is to say they must be immutable and have a less-than comparison.

    It's recommended to only insert keys which are all the same type, ensuring that they
    have a well-ordering. However, keys of different types can be inserted as long as
    their `__eq__` and `__lt__` methods behave.

    This class provides no protections against poorly behaved keys and can fail in an
    undefined manner if keys are not implemented properly.

    # Values
    Values can be any Python object.

    # Recursion
    This class does not use recursive techniques. This ensures that this package can be
    used on platforms with low recursion limits, even in scenarios with very large and
    very deep trees.

    # Time Complexities
    Time complexities for specific methods can be found in their docstrings.
    """

    def __init__(self, mapping: Mapping[_K, _V] | None = None) -> None:
        """Constructor.

        Inserting the elements of a passed-in mapping has an amortized and worst-case
        time complexity of O[n*log(n)].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> avl_tree
        AvlTree({0: 'a', 1: 'b'})
        ```

        Args:
            mapping (dict[_K, _V] | None): An optional initial mapping of items to add
                to this tree. Defaults to None.
        """
        self.__nodes: Final[dict[_K, AvlTreeNode[_K, _V]]] = {}
        self.__root_key: _K | None = None
        if mapping is not None:
            for key, value in mapping.items():
                self[key] = value

    def __setitem__(self, __k: _K, __v: _V) -> None:
        """Maps the given key to the given value in this tree.

        This method has an amortized and worst-case time complexity of O[log(n)].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> avl_tree[0] = 'foo'
        >>> avl_tree[2] = 'c'
        >>> avl_tree
        AvlTree({0: 'foo', 1: 'b', 2: 'c'})
        ```

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
        stack: Final[list[_K]] = [self.__root_key]
        current_node: AvlTreeNode[_K, _V] = self.__nodes[stack[-1]]
        while True:
            if __k < stack[-1] and current_node.lesser_child_key is None:
                current_node.lesser_child_key = __k
                self.__nodes[__k] = AvlTreeNode[_K, _V](value=__v)
                break
            if stack[-1] < __k and current_node.greater_child_key is None:
                current_node.greater_child_key = __k
                self.__nodes[__k] = AvlTreeNode[_K, _V](value=__v)
                break
            if __k < stack[-1] and current_node.lesser_child_key is not None:
                stack.append(current_node.lesser_child_key)
                current_node = self.__nodes[stack[-1]]
            elif current_node.greater_child_key is not None:
                stack.append(current_node.greater_child_key)
                current_node = self.__nodes[stack[-1]]
        self.__enforce_avl(stack=stack)

    def __delitem__(self, __k: _K) -> None:  # noqa: C901, PLR0912
        """Deletes the given key from this tree.

        This method has an amortized and worst-case time complexity of O[log(n)].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> del avl_tree[0]
        >>> avl_tree
        AvlTree({1: 'b'})
        ```

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
        stack: Final[list[_K]] = [node_key]
        node: AvlTreeNode[_K, _V] = self.__nodes[node_key]
        while node_key != __k:
            parent = node
            node_key = self.__get_closer_key(key=__k, current_key=node_key)
            stack.append(node_key)
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
                stack.append(replacement_key)
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
        if replacement_key is None:
            stack.remove(node_key)
        else:
            stack[stack.index(node_key)] = replacement_key
        self.__enforce_avl(stack=stack)

    def __getitem__(self, __k: _K) -> _V:
        """Gets the value associated with the given key.

        This method has an amortized and worst-case time complexity of O[log(n)].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> avl_tree[0]
        'a'
        >>> avl_tree[2]
        KeyError: 'Key not present in AvlTree: 2'
        ```

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

        This method has an amortized and worst-case time complexity of O[1].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> len(avl_tree)
        2
        ```

        Returns:
            int: The number of items contained in this tree.
        """
        return len(self.__nodes)

    def __iter__(self) -> Iterator[_K]:
        """Iterates over all keys contained in this tree in sort order.

        Getting the first key has an amortized and worst-case time complexity of
        O[log(n)]. Iterating over all keys has an amortized and worst-case time
        complexity of O[n].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> for key in avl_tree:
        ...     print(key)
        ...
        0
        1
        ```

        Returns:
            Iterator[_K]: The iterator object.
        """
        return self.between()

    def __repr__(self) -> str:
        """Builds a developer-friendly string representation of this AvlTree.

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> repr(avl_tree)
        "AvlTree({0: 'a', 1: 'b'})"
        ```

        Returns:
            str: A string representation of this AvlTree.
        """
        return f"AvlTree({{{', '.join(f'{k!r}: {v!r}' for k, v in self.items())}}})"

    def minimum(self) -> _K:
        """Gets the minimum key contained in this tree.

        This method has an amortized and worst-case time complexity of O[log(n)].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> avl_tree.minimum()
        0
        ```

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

        This method has an amortized and worst-case time complexity of O[log(n)].

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b'})
        >>> avl_tree.maximum()
        1
        ```

        Returns:
            _K: The maximum key.

        Raises:
            ValueError: If there are no keys present in this tree.
        """
        if self.__root_key is None:
            message: Final[str] = "Cannot get the maximum of an empty AvlTree"
            raise ValueError(message)
        key: _K = self.__root_key
        node: AvlTreeNode[_K, _V] = self.__nodes[key]
        while node.greater_child_key is not None:
            key = node.greater_child_key
            node = self.__nodes[key]
        return key

    def between(  # noqa: C901, PLR0912
        self,
        start: _K | None = None,
        stop: _K | None = None,
        treatment: Literal["inclusive", "exclusive"] = "inclusive",
    ) -> Iterator[_K]:
        """Iterates over all keys between the given start and stop in sort order.

        Getting the first key has an amortized and worst-case time complexity of
        O[log(n)]. Iterating over all keys has an amortized and worst-case time
        complexity of O[k], where k is the number of items in only the interval between
        start and stop.

        Example usage:
        ```
        >>> from avltree import AvlTree
        >>> avl_tree = AvlTree[int, str]({0: 'a', 1: 'b', 2: 'c'})
        >>> for key in avl_tree.between(start=0, stop=2, treatment="inclusive"):
        ...     print(key)
        ...
        0
        1
        2
        >>> for key in avl_tree.between(start=0, treatment="exclusive"):
        ...     print(key)
        ...
        1
        2
        ```

        Args:
            start (_K | None): The key at which to start iterating. If None, iteration
                starts at the minimum key. Defaults to None.
            stop (_K | None): The key at which to stop iterating. If None, iteration
                stops at the maximum key. Defaults to None.
            treatment (Literal["inclusive", "exclusive"]): Whether the given start and
                stop should be included or excluded from the returned iterator. Has no
                effect when start and stop are None. Defaults to "inclusive".

        Returns:
            Iterator[_K]: An iterator which will iterate over all keys between the given
                start and stop.
        """
        if self.__root_key is None:
            return
        stack: Final[list[tuple[_K, bool]]] = []
        current_key: _K = self.__root_key
        while True:
            current_node: AvlTreeNode[_K, _V] = self.__nodes[current_key]
            if start is None or start < current_key:
                stack.append((current_key, True))
                if current_node.lesser_child_key is not None:
                    current_key = current_node.lesser_child_key
                else:
                    break
            elif start == current_key:
                if treatment == "inclusive":
                    stack.append((current_key, True))
                    break
                elif current_node.greater_child_key is not None:
                    current_key = current_node.greater_child_key
                else:
                    break
            elif current_node.greater_child_key is not None:
                current_key = current_node.greater_child_key
            else:
                break
        while len(stack) > 0:
            key, lesser_child_visited = stack.pop(-1)
            node: AvlTreeNode[_K, _V] = self.__nodes[key]
            if (
                stop is not None  # noqa: PLR0916
                and (stop < key or (stop == key and treatment == "exclusive"))
                and (lesser_child_visited or node.lesser_child_key is None)
            ):
                break
            elif node.lesser_child_key is not None and not lesser_child_visited:
                stack.append((key, True))
                stack.append((node.lesser_child_key, False))
            elif node.greater_child_key is not None:
                stack.append((node.greater_child_key, False))
                yield key
            else:
                yield key

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

    def __enforce_avl(self, stack: list[_K]) -> None:
        """Enforces the AVL property on this tree.

        Args:
            stack (list[_K]): The stack to traverse in reverse order.
        """
        while len(stack) > 0:
            key: _K = stack.pop(-1)
            node: AvlTreeNode[_K, _V] = self.__nodes[key]
            balance: int = self.__calculate_balance(node=node)
            if -1 <= balance <= 1:
                self.__update_height(node=node)
                continue
            if balance == -2:  # noqa: PLR2004
                lesser_child_key: _K = cast(_K, node.lesser_child_key)
                if self.__calculate_balance(node=self.__nodes[lesser_child_key]) == 1:
                    node.lesser_child_key = self.__rotate(
                        key=lesser_child_key,
                        direction="left",
                    )
                replacement_key: _K = self.__rotate(key=key, direction="right")
            else:
                greater_child_key: _K = cast(_K, node.greater_child_key)
                if self.__calculate_balance(node=self.__nodes[greater_child_key]) == -1:
                    node.greater_child_key = self.__rotate(
                        key=greater_child_key,
                        direction="right",
                    )
                replacement_key = self.__rotate(key=key, direction="left")
            parent_node: AvlTreeNode[_K, _V] | None = (
                None if len(stack) == 0 else self.__nodes[stack[-1]]
            )
            if parent_node is None:
                self.__root_key = replacement_key
            elif parent_node.lesser_child_key == key:
                parent_node.lesser_child_key = replacement_key
            else:
                parent_node.greater_child_key = replacement_key

    def __calculate_balance(self, node: AvlTreeNode[_K, _V]) -> int:
        """Calculates the balance factor of the given node.

        Args:
            node (AvlTreeNode[_K, _V]): The node.

        Returns:
            int: The balance factor of the given node.
        """
        return (
            -1
            if node.greater_child_key is None
            else self.__nodes[node.greater_child_key].height
        ) - (
            -1
            if node.lesser_child_key is None
            else self.__nodes[node.lesser_child_key].height
        )

    def __update_height(self, node: AvlTreeNode[_K, _V]) -> None:
        """Updates the height of the given node.

        Args:
            node (AvlTreeNode[_K, _V]): The node.
        """
        node.height = 1 + max(
            (
                -1
                if node.greater_child_key is None
                else self.__nodes[node.greater_child_key].height
            ),
            (
                -1
                if node.lesser_child_key is None
                else self.__nodes[node.lesser_child_key].height
            ),
        )

    def __rotate(self, key: _K, direction: Literal["left", "right"]) -> _K:
        """Performs a rotation at the given key.

        Args:
            key (_K): The key to perform a right rotation on.
            direction (Literal["left", "right"]): The direction of the rotation.

        Returns:
            _K: The new root key of this subtree.

        Raises:
            ValueError: If the shape of the tree is incompatible with the requested
                rotation direction.
        """
        node: Final[AvlTreeNode[_K, _V]] = self.__nodes[key]
        replacement_key: Final[_K] = cast(
            _K,
            node.greater_child_key if direction == "left" else node.lesser_child_key,
        )
        replacement_node: Final[AvlTreeNode[_K, _V]] = self.__nodes[replacement_key]
        if direction == "left":
            node.greater_child_key = replacement_node.lesser_child_key
            replacement_node.lesser_child_key = key
        else:
            node.lesser_child_key = replacement_node.greater_child_key
            replacement_node.greater_child_key = key
        self.__update_height(node=node)
        self.__update_height(node=replacement_node)
        return replacement_key
