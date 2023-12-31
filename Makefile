test:
	pipenv run coverage run -m pytest -vv
	pipenv run coverage report -m

test-verbose:
	pipenv run pytest -vv -s --log-cli-level INFO

lint: black mypy ruff

black:
	pipenv run black --check --diff .

mypy:
	pipenv run mypy .

ruff:
	pipenv run ruff check .

lint-apply: black-apply mypy ruff-apply

black-apply:
	pipenv run black .

ruff-apply:
	pipenv run ruff check --fix .

example:
	PYTHONPATH=. pipenv run python examples/$(name).py