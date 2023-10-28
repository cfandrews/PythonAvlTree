rm -rf .mypy_cache .pytest_cache .ruff_cache ./src/avltree.egg-info venv .coverage pyvenv.cfg dist
set -e
python3 -m venv venv
./venv/bin/pip install -e '.[build]'
./venv/bin/pre-commit install
./venv/bin/isort .
./venv/bin/ruff format ./src
./venv/bin/ruff format ./tests
./venv/bin/ruff check ./src
./venv/bin/ruff check ./tests
./venv/bin/mypy
./venv/bin/pytest
./venv/bin/python3 -m build