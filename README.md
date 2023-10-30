# Python AVL Tree
[![Stable Version](https://img.shields.io/pypi/v/avltree?color=blue)](https://pypi.org/project/avltree/)
[![Build Status](https://github.com/cfandrews/PythonAvlTree/actions/workflows/build.yml/badge.svg)](https://github.com/cfandrews/PythonAvlTree/actions)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This package is a lightweight, pure-Python implementation of the AVL tree. AVL trees are simple self-balancing binary
search trees, giving them both amortized and worst-case time complexities of O[log(n)] for insertion, deletion, and
retrieval. More reference can be found on the [AVL tree Wikipedia page](https://en.wikipedia.org/wiki/AVL_tree).

[PyPI](https://pypi.org/project/avltree/)\
[Source](https://github.com/cfandrews/PythonAvlTree)

## Installation
This package is available on PyPI and can be installed with pip:
```shell
pip install avltree
```

## Documentation
### Usage
The `AvlTree` class implements the [MutableMapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping)
generic interface and can be used in (almost) the exact same way as the [dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
built-in collection.

Basic dictionary-esque usage looks like:
```python
from avltree import AvlTree
avl_tree: AvlTree[int, str] = AvlTree[int, str]({2: "c", 1: "b", 0: "a"})
print(avl_tree)
# AvlTree({0: 'a', 1: 'b', 2: 'c'})

print(avl_tree[0])
# a

print(len(avl_tree))
# 3

avl_tree[3] = "d"
print(avl_tree)
# AvlTree({0: 'a', 1: 'b', 2: 'c', 3: 'd'})

del avl_tree[3]
print(avl_tree)
# AvlTree({0: 'a', 1: 'b', 2: 'c'})
```

Unlike dictionaries, the keys of an `AvlTree` instance can be iterated on in sort-order, and all methods which return
iterators are guaranteed to be sorted by key:
```python
from avltree import AvlTree
avl_tree: AvlTree[int, str] = AvlTree[int, str]({2: "c", 1: "b", 0: "a"})
for key in avl_tree:
    print(key)
# 0
# 1
# 2

for value in avl_tree.values():
    print(value)
# a
# b
# c

for key, value in avl_tree.items():
    print(key, value)
# 0 a
# 1 b
# 2 c
```

`AvlTree` instances also have helper methods for retrieving the minimum and maximum keys and performing inequality
operations on the set of all keys:
```python
from avltree import AvlTree
avl_tree: AvlTree[int, str] = AvlTree[int, str](
    {5: "f", 4: "e", 3: "d", 2: "c", 1: "b", 0: "a"}
)
print(avl_tree.minimum())
# 0

print(avl_tree.maximum())
# 5

for key in avl_tree.between(start=0, stop=4, treatment="exclusive"):
    print(key)
# 1
# 2
# 3

for key in avl_tree.between(start=0, stop=4, treatment="inclusive"):
    print(key)
# 0
# 1
# 2
# 3
# 4
```

### Keys
Anything used as a key in an `AvlTree` must implement `__eq__`, `__hash__`, and `__lt__`. That is to say they must be
immutable and have a less-than comparison.

It's recommended to only insert keys which are all the same type, ensuring that they have a well-ordering. However,
keys of different types can be inserted as long as their `__eq__` and `__lt__` methods behave.

This package provides no protections against poorly behaved keys and can fail in an undefined manner if keys are not
implemented properly.

### Values
Values can be any Python object.

### Recursion
The `AvlTree` class does not use recursive techniques. This ensures that this package can be used on platforms with low
recursion limits, even in scenarios with very large and very deep trees.
