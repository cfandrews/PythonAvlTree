# Copyright 2023 Charles Andrews
"""Unit tests for _avl_tree."""
from __future__ import annotations  # noqa: I001

from dataclasses import dataclass
from random import shuffle
from typing import Final, Literal

import pytest
from assertpy import assert_that

from avltree import AvlTree
from avltree._avl_tree_node import AvlTreeNode


def _construct_avl_tree(items: list[tuple[int, str]]) -> AvlTree[int, str]:
    """Constructs an AvlTree containing the given items inserted in the given order.

    Args:
        items (list[tuple[int, str]]): The items to add to the AvlTree.

    Returns:
        AvlTree[int, str]: The AvlTree.
    """
    avl_tree: Final[AvlTree[int, str]] = AvlTree[int, str]()
    for key, value in items:
        avl_tree[key] = value
    return avl_tree


def _copy_avl_tree(avl_tree: AvlTree[int, str]) -> AvlTree[int, str]:
    """Creates a copy of an existing AvlTree.

    Args:
        avl_tree (AvlTree[int, str]): The AvlTree to copy.

    Returns:
        AvlTree[int, str]: The new AvlTree.
    """
    copy_avl_tree: Final[AvlTree[int, str]] = AvlTree[int, str]()
    setattr(  # noqa: B010
        copy_avl_tree,
        "_AvlTree__root_key",
        getattr(avl_tree, "_AvlTree__root_key"),  # noqa: B009
    )
    nodes: Final[dict[int, AvlTreeNode[int, str]]] = getattr(  # noqa: B009
        avl_tree,
        "_AvlTree__nodes",
    )
    copy_nodes: Final[dict[int, AvlTreeNode[int, str]]] = {}
    for key, node in nodes.items():
        copy_nodes[key] = AvlTreeNode[int, str](value=node.value)
        copy_nodes[key].lesser_child_key = node.lesser_child_key
        copy_nodes[key].greater_child_key = node.greater_child_key
    setattr(copy_avl_tree, "_AvlTree__nodes", copy_nodes)  # noqa: B010
    return copy_avl_tree


@dataclass(frozen=True)
class _Modification:
    """Represents a modification to the structure of an AvlTree."""

    modification_type: Literal["root", "lesser", "greater", "value"]
    key: int | None = None
    initial: int | str | None = None
    modified: int | str | None = None

    def __post_init__(self) -> None:
        """Validates that the properties of this _Modification.

        Raises:
            ValueError: If the properties of this _Modification are invalid.
        """
        if self.modification_type == "root" and self.key is not None:
            raise ValueError
        if self.modification_type != "root" and self.key is None:
            raise ValueError


def _get_modifications(
    initial_avl_tree: AvlTree[int, str],
    modified_avl_tree: AvlTree[int, str],
) -> list[_Modification]:
    """Determines the difference between two AvlTrees.

    Args:
        initial_avl_tree (AvlTree[int, str]): The initial AvlTree.
        modified_avl_tree (AvlTree[int, str]): The modified AvlTree.

    Returns:
        list[_Modification]: The difference between the two given AvlTrees.
    """
    modifications: Final[list[_Modification]] = []
    initial_root_key: Final[int | None] = getattr(  # noqa: B009
        initial_avl_tree,
        "_AvlTree__root_key",
    )
    modified_root_key: Final[int | None] = getattr(  # noqa: B009
        modified_avl_tree,
        "_AvlTree__root_key",
    )
    initial_nodes: Final[dict[int, AvlTreeNode[int, str]]] = getattr(  # noqa: B009
        initial_avl_tree,
        "_AvlTree__nodes",
    )
    modified_nodes: Final[dict[int, AvlTreeNode[int, str]]] = getattr(  # noqa: B009
        modified_avl_tree,
        "_AvlTree__nodes",
    )
    if initial_root_key != modified_root_key:
        modifications.append(
            _Modification(
                modification_type="root",
                initial=None if initial_root_key is None else initial_root_key,
                modified=None if modified_root_key is None else modified_root_key,
            ),
        )
    for key in initial_nodes.keys() & modified_nodes.keys():
        if initial_nodes[key].lesser_child_key != modified_nodes[key].lesser_child_key:
            modifications.append(
                _Modification(
                    modification_type="lesser",
                    key=key,
                    initial=None
                    if initial_nodes[key].lesser_child_key is None
                    else initial_nodes[key].lesser_child_key,
                    modified=None
                    if modified_nodes[key].lesser_child_key is None
                    else modified_nodes[key].lesser_child_key,
                ),
            )
        if (
            initial_nodes[key].greater_child_key
            != modified_nodes[key].greater_child_key
        ):
            modifications.append(
                _Modification(
                    modification_type="greater",
                    key=key,
                    initial=None
                    if initial_nodes[key].greater_child_key is None
                    else initial_nodes[key].greater_child_key,
                    modified=None
                    if modified_nodes[key].greater_child_key is None
                    else modified_nodes[key].greater_child_key,
                ),
            )
        if initial_nodes[key].value != modified_nodes[key].value:
            modifications.append(
                _Modification(
                    modification_type="value",
                    key=key,
                    initial=initial_nodes[key].value,
                    modified=modified_nodes[key].value,
                ),
            )
    return modifications


def assert_avl_tree_shape(avl_tree: AvlTree[int, str], keys: list[int]) -> None:
    """Asserts that the given AvlTree has a valid AVL shape.

    Args:
        avl_tree (AvlTree[int, str]): The AvlTree to validate.
        keys (list[int]): The keys which should be present in the tree.

    Raises:
        AssertionError: If the keys are in the incorrect order or if the tree does not
            have a valid AVL shape.
    """
    assert_that(list(avl_tree)).is_equal_to(sorted(keys))
    nodes: dict[int, AvlTreeNode[int, str]] = getattr(  # noqa: B009
        avl_tree,
        "_AvlTree__nodes",
    )
    for node in nodes.values():
        assert_that(
            getattr(avl_tree, "_AvlTree__calculate_balance")(  # noqa: B009
                node=node,
            ),
        ).is_between(-1, 1)
        assert_that(
            1
            + max(
                -1
                if node.lesser_child_key is None
                else nodes[node.lesser_child_key].height,
                -1
                if node.greater_child_key is None
                else nodes[node.greater_child_key].height,
            ),
        ).is_equal_to(node.height)


class TestAvlTree:
    """Unit tests for AvlTree."""

    @staticmethod
    @pytest.mark.parametrize("initial_items", [None, {}, {0: "0"}, {0: "0", 1: "1"}])
    def test_init(initial_items: dict[int, str] | None) -> None:
        """Tests happy path cases of AvlTree.__init__().

        Args:
            initial_items (dict[int, str] | None): The initial items to pass into the
                constructor.
        """
        avl_tree: Final[AvlTree[int, str]] = AvlTree(initial_items=initial_items)
        if initial_items is None:
            assert_that(list(avl_tree)).is_empty()
        else:
            assert_that(list(avl_tree)).is_equal_to(sorted(initial_items.keys()))

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "key", "value", "expected_modifications"),
        [
            ([], 0, "0", [_Modification(modification_type="root", modified=0)]),
            (
                [(0, "0")],
                0,
                "1",
                [
                    _Modification(
                        modification_type="value",
                        key=0,
                        initial="0",
                        modified="1",
                    ),
                ],
            ),
            (
                [(1, "1")],
                0,
                "0",
                [
                    _Modification(
                        modification_type="lesser",
                        key=1,
                        modified=0,
                    ),
                ],
            ),
            (
                [(0, "0")],
                1,
                "1",
                [
                    _Modification(
                        modification_type="greater",
                        key=0,
                        modified=1,
                    ),
                ],
            ),
            (
                [(2, "2"), (1, "1"), (3, "3")],
                0,
                "0",
                [
                    _Modification(
                        modification_type="lesser",
                        key=1,
                        modified=0,
                    ),
                ],
            ),
            (
                [(1, "1"), (0, "0"), (2, "2")],
                3,
                "3",
                [
                    _Modification(
                        modification_type="greater",
                        key=2,
                        modified=3,
                    ),
                ],
            ),
            (
                [(2, "2"), (1, "1")],
                0,
                "0",
                [
                    _Modification(
                        modification_type="root",
                        initial=2,
                        modified=1,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=2,
                        initial=1,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=1,
                        modified=2,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=1,
                        modified=0,
                    ),
                ],
            ),
            (
                [(2, "2"), (0, "0")],
                1,
                "1",
                [
                    _Modification(
                        modification_type="root",
                        initial=2,
                        modified=1,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=2,
                        initial=0,
                    ),
                ],
            ),
            (
                [(0, "0"), (1, "1")],
                2,
                "2",
                [
                    _Modification(
                        modification_type="root",
                        initial=0,
                        modified=1,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=0,
                        initial=1,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=1,
                        modified=0,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=1,
                        modified=2,
                    ),
                ],
            ),
            (
                [(0, "0"), (2, "2")],
                1,
                "1",
                [
                    _Modification(
                        modification_type="root",
                        initial=0,
                        modified=1,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=0,
                        initial=2,
                    ),
                ],
            ),
            (
                [(3, "3"), (2, "2"), (4, "4"), (1, "1")],
                0,
                "0",
                [
                    _Modification(
                        modification_type="lesser",
                        key=3,
                        initial=2,
                        modified=1,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=2,
                        initial=1,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=1,
                        modified=2,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=1,
                        modified=0,
                    ),
                ],
            ),
            (
                [(1, "1"), (0, "0"), (2, "2"), (3, "3")],
                4,
                "4",
                [
                    _Modification(
                        modification_type="greater",
                        key=1,
                        initial=2,
                        modified=3,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=2,
                        initial=3,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=3,
                        modified=2,
                    ),
                    _Modification(
                        modification_type="greater",
                        key=3,
                        modified=4,
                    ),
                ],
            ),
        ],
    )
    def test_setitem(
        items: list[tuple[int, str]],
        key: int,
        value: str,
        expected_modifications: list[_Modification],
    ) -> None:
        """Tests happy path cases of AvlTree.__setitem__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            key (int): The key to set in the AvlTree.
            value (str): The value to map to the key.
            expected_modifications (list[_Modification]): The expected modifications to
                the AvlTree.
        """
        initial_avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        modified_avl_tree: Final[AvlTree[int, str]] = _copy_avl_tree(
            avl_tree=initial_avl_tree,
        )
        modified_avl_tree[key] = value
        assert_that(
            getattr(modified_avl_tree, "_AvlTree__nodes"),  # noqa: B009
        ).contains_key(
            key,
        )
        actual_modifications: list[_Modification] = _get_modifications(
            initial_avl_tree=initial_avl_tree,
            modified_avl_tree=modified_avl_tree,
        )
        assert_that(actual_modifications).is_length(len(expected_modifications))
        for modification in expected_modifications:
            assert_that(actual_modifications).contains(modification)

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "key", "expected_modifications", "expected_stack"),
        [
            ([(0, "0")], 0, [_Modification(modification_type="root", initial=0)], []),
            (
                [(1, "1"), (0, "0")],
                0,
                [_Modification(modification_type="lesser", key=1, initial=0)],
                [1],
            ),
            (
                [(0, "0"), (1, "1")],
                1,
                [_Modification(modification_type="greater", key=0, initial=1)],
                [0],
            ),
            (
                [(1, "1"), (0, "0")],
                1,
                [_Modification(modification_type="root", initial=1, modified=0)],
                [0],
            ),
            (
                [(0, "0"), (1, "1")],
                0,
                [_Modification(modification_type="root", initial=0, modified=1)],
                [1],
            ),
            (
                [(1, "1"), (0, "0"), (2, "2")],
                1,
                [
                    _Modification(modification_type="root", initial=1, modified=2),
                    _Modification(modification_type="lesser", key=2, modified=0),
                ],
                [2],
            ),
            (
                [(1, "1"), (0, "0"), (3, "3"), (2, "2")],
                1,
                [
                    _Modification(modification_type="root", initial=1, modified=2),
                    _Modification(modification_type="lesser", key=2, modified=0),
                    _Modification(modification_type="greater", key=2, modified=3),
                    _Modification(modification_type="lesser", key=3, initial=2),
                ],
                [2, 3],
            ),
            (
                [(2, "2"), (1, "1"), (5, "5"), (0, "0"), (3, "3"), (6, "6"), (4, "4")],
                2,
                [
                    _Modification(modification_type="root", initial=2, modified=3),
                    _Modification(modification_type="lesser", key=3, modified=1),
                    _Modification(
                        modification_type="greater",
                        key=3,
                        initial=4,
                        modified=5,
                    ),
                    _Modification(
                        modification_type="lesser",
                        key=5,
                        initial=3,
                        modified=4,
                    ),
                ],
                [3, 5],
            ),
        ],
    )
    def test_delitem(
        items: list[tuple[int, str]],
        key: int,
        expected_modifications: list[_Modification],
        expected_stack: list[int],
    ) -> None:
        """Tests happy path cases of AvlTree.__delitem__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            key (int): The key to delete from the AvlTree.
            expected_modifications (list[_Modification]): The expected modifications to
                the AvlTree.
            expected_stack (list[int]): The stack which is expected to be passed to
                AvlTree.__enforce_avl.
        """
        initial_avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        modified_avl_tree: Final[AvlTree[int, str]] = _copy_avl_tree(
            avl_tree=initial_avl_tree,
        )
        assert_that(
            getattr(modified_avl_tree, "_AvlTree__nodes"),  # noqa: B009
        ).contains_key(
            key,
        )
        setattr(  # noqa: B010
            modified_avl_tree,
            "_AvlTree__enforce_avl",
            lambda stack: assert_that(stack).is_equal_to(expected_stack),
        )
        del modified_avl_tree[key]
        assert_that(
            getattr(modified_avl_tree, "_AvlTree__nodes"),  # noqa: B009
        ).does_not_contain_key(
            key,
        )
        actual_modifications: list[_Modification] = _get_modifications(
            initial_avl_tree=initial_avl_tree,
            modified_avl_tree=modified_avl_tree,
        )
        assert_that(actual_modifications).is_length(len(expected_modifications))
        for modification in expected_modifications:
            assert_that(actual_modifications).contains(modification)

    @staticmethod
    @pytest.mark.parametrize(("items", "key"), [([], 0), ([(0, "0")], 1)])
    def test_delitem_key_error(items: list[tuple[int, str]], key: int) -> None:
        """Tests KeyError cases of AvlTree.__delitem__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            key (int): The key to delete from the AvlTree.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        assert_that(
            getattr(avl_tree, "_AvlTree__nodes"),  # noqa: B009
        ).does_not_contain_key(
            key,
        )
        with pytest.raises(KeyError):
            del avl_tree[key]

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "key", "value"),
        [
            ([(0, "0")], 0, "0"),
            ([(1, "1"), (0, "0")], 0, "0"),
            ([(0, "0"), (1, "1")], 1, "1"),
        ],
    )
    def test_getitem(items: list[tuple[int, str]], key: int, value: str) -> None:
        """Tests happy path cases of AvlTree.__getitem__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            key (int): The key to get.
            value (str): The value to expect.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        assert_that(avl_tree[key]).is_equal_to(value)

    @staticmethod
    @pytest.mark.parametrize(("items", "key"), [([], 0), ([(0, "0")], 1)])
    def test_getitem_key_error(items: list[tuple[int, str]], key: int) -> None:
        """Tests KeyError cases of AvlTree.__getitem__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            key (int): The key to get.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        with pytest.raises(KeyError):
            avl_tree[key]

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "length"),
        [([], 0), ([(0, "0")], 1), ([(0, "0"), (1, "1")], 2)],
    )
    def test_len(items: list[tuple[int, str]], length: int) -> None:
        """Tests happy path cases of AvlTree.__len__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            length (int): The expected length of the AvlTree.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        assert_that(avl_tree).is_length(length)

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "sorted_keys"),
        [
            ([], []),
            ([(0, "0")], [0]),
            ([(1, "1"), (0, "0")], [0, 1]),
            ([(0, "0"), (1, "1")], [0, 1]),
            ([(1, "1"), (0, "0"), (2, "2")], [0, 1, 2]),
        ],
    )
    def test_iter(items: list[tuple[int, str]], sorted_keys: list[int]) -> None:
        """Tests happy path cases of AvlTree.__iter__().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            sorted_keys (list[int]): The expected keys in sort order.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        assert_that(list(avl_tree)).is_equal_to(sorted_keys)

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "minimum"),
        [([(0, "0")], 0), ([(1, "1"), (0, "0")], 0)],
    )
    def test_minimum(items: list[tuple[int, str]], minimum: int) -> None:
        """Tests happy path cases of AvlTree.minimum().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            minimum (int): The expected minimum of the AvlTree.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        assert_that(avl_tree.minimum()).is_equal_to(minimum)

    @staticmethod
    def test_minimum_value_error() -> None:
        """Tests ValueError cases of AvlTree.minimum()."""
        avl_tree: Final[AvlTree[int, str]] = AvlTree[int, str]()
        with pytest.raises(
            ValueError,
            match=r"Cannot get the minimum of an empty AvlTree",
        ):
            avl_tree.minimum()

    @staticmethod
    @pytest.mark.parametrize(
        ("items", "maximum"),
        [([(0, "0")], 0), ([(0, "0"), (1, "1")], 1)],
    )
    def test_maximum(items: list[tuple[int, str]], maximum: int) -> None:
        """Tests happy path cases of AvlTree.maximum().

        Args:
            items (list[tuple[int, str]]): The initial items in the AvlTree.
            maximum (int): The expected maximum of the AvlTree.
        """
        avl_tree: Final[AvlTree[int, str]] = _construct_avl_tree(items=items)
        assert_that(avl_tree.maximum()).is_equal_to(maximum)

    @staticmethod
    def test_maximum_value_error() -> None:
        """Tests ValueError cases of AvlTree.maximum()."""
        avl_tree: Final[AvlTree[int, str]] = AvlTree[int, str]()
        with pytest.raises(
            ValueError,
            match=r"Cannot get the maximum of an empty AvlTree",
        ):
            avl_tree.maximum()

    @staticmethod
    def test_large_scale() -> None:
        """Tests a large scale case of adding and deleting many items."""
        keys: Final[list[int]] = list(range(1000))
        shuffle(keys)
        avl_tree: Final[AvlTree[int, str]] = AvlTree()
        for i, key in enumerate(keys):
            avl_tree[key] = str(key)
            assert_avl_tree_shape(avl_tree=avl_tree, keys=keys[: i + 1])
        for i, key in enumerate(keys):
            del avl_tree[key]
            assert_avl_tree_shape(avl_tree=avl_tree, keys=keys[i + 1 :])
