rm -rf ./build ./src/avltree.egg-info
set -e
python3 -m venv ./build/venv
./build/venv/bin/pip install -e '.[build]'
./build/venv/bin/pre-commit install
./build/venv/bin/isort ./src
./build/venv/bin/isort ./tests
./build/venv/bin/ruff format ./src
./build/venv/bin/ruff format ./tests
./build/venv/bin/ruff check ./src
./build/venv/bin/ruff check ./tests
./build/venv/bin/mypy --cache-dir ./build/mypy
./build/venv/bin/pytest
./build/venv/bin/pdoc ./src/avltree -o ./build/pdoc
./build/venv/bin/python3 -m build --outdir ./build/build