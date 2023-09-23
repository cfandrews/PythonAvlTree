# Copyright 2023 Charles Andrews
"""Unit tests for _avl_tree."""
from __future__ import annotations  # noqa: I001

from typing import Final

import pytest
from assertpy import assert_that

from avltree import AvlTree


def _construct_avl_tree(elements: list[int]) -> AvlTree[int]:
    """Constructs an AvlTree containing the given elements.

    Args:
        elements (list[int]): The elements to add to the AvlTree.

    Returns:
        AvlTree[int]: The AvlTree.
    """
    avl_tree: Final[AvlTree[int]] = AvlTree[int]()
    for element in elements:
        avl_tree.add(element)
    return avl_tree


class TestAvlTree:
    """Unit tests for AvlTree."""

    @staticmethod
    @pytest.mark.parametrize(
        "elements",
        [[], [0], [1, 0], [0, 1], [1, 0, 2], [1, 2, 0], [0, 0], [1, 0, 0], [0, 1, 1]],
    )
    def test_add(elements: list[int]) -> None:
        """Tests happy path cases of AvlTree.add().

        Args:
            elements (list[int]): The elements to add to the AvlTree.
        """
        avl_tree: Final[AvlTree[int]] = _construct_avl_tree(elements=elements)
        assert_that(list(avl_tree)).is_equal_to(sorted(set(elements)))

    @staticmethod
    @pytest.mark.parametrize(
        ("initial_elements", "elements_to_discard", "expected_elements"),
        [
            ([], [0], []),
            ([0], [0], []),
            ([1, 0], [1], [0]),
            ([0, 1], [0], [1]),
            ([1, 0, 2], [1], [0, 2]),
            ([1, 0, 2, 3], [1], [0, 2, 3]),
            ([1, 0, 3, 2], [1], [0, 2, 3]),
            ([2, 0, 1, 5, 3, 4], [2], [0, 1, 3, 4, 5]),
            ([1, 0], [0], [1]),
            ([0, 1], [1], [0]),
            ([1, 0, 2], [0], [1, 2]),
            ([1, 0, 2], [2], [0, 1]),
            ([1, 0, 3, 2], [3], [0, 1, 2]),
            ([1, 0], [2], [0, 1]),
            ([1, 2], [0], [1, 2]),
            ([2, 1], [0], [1, 2]),
            ([0, 2], [1], [0, 2]),
        ],
    )
    def test_discard(
        initial_elements: list[int],
        elements_to_discard: list[int],
        expected_elements: list[int],
    ) -> None:
        """Tests happy path cases of AvlTree.discard().

        Args:
            initial_elements (list[int]): The initial elements of the AvlTree.
            elements_to_discard (list[int]): The elements to discard from the AvlTree.
            expected_elements (list[int]): The (sorted) elements to expect in the
                AvlTree.
        """
        avl_tree: Final[AvlTree[int]] = _construct_avl_tree(elements=initial_elements)
        for element in elements_to_discard:
            avl_tree.discard(value=element)
        assert_that(list(avl_tree)).is_equal_to(expected_elements)

    @staticmethod
    @pytest.mark.parametrize(
        ("elements", "element_to_test", "should_be_contained"),
        [
            ([], 0, False),
            ([0], 0, True),
            ([1], 0, False),
            ([0], 1, False),
            ([0], "", False),
            ([1, 0], 0, True),
            ([0, 1], 1, True),
        ],
    )
    def test_contains(
        elements: list[int],
        element_to_test: object,
        should_be_contained: bool,  # noqa: FBT001
    ) -> None:
        """Tests happy path cases of AvlTree.__contains__().

        Args:
            elements (list[int]): The elements of the AvlTree.
            element_to_test (int): The element to test for inclusion in the AvlTree.
            should_be_contained (bool): Whether the given element should be contained in
                the AvlTree.
        """
        avl_tree: Final[AvlTree[int]] = _construct_avl_tree(elements=elements)
        assert_that(element_to_test in avl_tree).is_equal_to(should_be_contained)

    @staticmethod
    @pytest.mark.parametrize(
        ("elements", "expected_length"),
        [([], 0), ([0], 1), ([0, 1], 2), ([0, 1, 2], 3)],
    )
    def test_len(elements: list[int], expected_length: int) -> None:
        """Tests happy path cases of AvlTree.len().

        Args:
            elements (list[int]): The elements of the AvlTree.
            expected_length (int): The expected length of the AvlTree.
        """
        avl_tree: Final[AvlTree[int]] = _construct_avl_tree(elements=elements)
        assert_that(len(avl_tree)).is_equal_to(expected_length)

    @staticmethod
    @pytest.mark.parametrize(
        "elements",
        [
            [],
            [0],
            [1, 0],
            [0, 1],
            [1, 0, 2],
            [2, 0, 1, 3],
            [2, 1, 0, 3],
            [3, 1, 0, 2, 4],
        ],
    )
    def test_iter(elements: list[int]) -> None:
        """Tests happy path cases of AvlTree.__iter__().

        Args:
            elements (list[int]): The elements of the AvlTree.
        """
        avl_tree: Final[AvlTree[int]] = _construct_avl_tree(elements=elements)
        assert_that(list(avl_tree)).is_equal_to(sorted(set(elements)))
