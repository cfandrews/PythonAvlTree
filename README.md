# Python AVL Tree
[![Stable Version](https://img.shields.io/pypi/v/avltree?color=blue)](https://pypi.org/project/avltree/)
[![Build Status](https://github.com/cfandrews/PythonAvlTree/actions/workflows/build.yml/badge.svg)](https://github.com/cfandrews/PythonAvlTree/actions)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This package is a lightweight, pure-Python implementation of the AVL tree. AVL trees are simple self-balancing binary
search trees, giving them both amortized and worst-case time complexities of O(logn) for insertion, deletion, and
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
The `AvlTree` class implements the `MutableMapping` generic interface and can be instantiated with or without generic
arguments. `AvlTree` objects can also optionally be instantiated from a pre-existing dictionary of items by passing the
dictionary  to the constructor:
```
>>> from avltree import AvlTree
>>> avl_tree: AvlTree[int, str] = AvlTree[int, str]({0: "0", 1: "1"})
>>> list(avl_tree)
[0, 1]
```

Adding a new item to an `AvlTree` can be done with the same bracket notation as any dictionary:
```
>>> avl_tree[2] = "2"
>>> list(avl_tree)
[0, 1, 2]
```

The same is true of deletion:
```
>>> del avl_tree[2]
>>> list(avl_tree)
[0, 1]
```

As well as retrieval:
```
>>> avl_tree[0]
'0'
```

Due to the internal implementation, getting the total size, i.e. number of items, of an `AvlTree` always has a constant
time complexity:
```
>>> len(avl_tree)
2
```

Similarly to a dictionary, iterating over an `AvlTree` iterates over its keys. Unlike a dictionary, the keys are
returned in sort-order:
```
>>> for key in avl_tree:
>>>     print(key)
>>>
0
1
```

`AvlTree` objects also provide helper methods for retrieving the minimum and maximum keys stored in the tree:
```
>>> avl_tree.minimum()
0
>>> avl_tree.maximum()
1
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
