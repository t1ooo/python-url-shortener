.PHONY: serve
serve:
	poetry run sanic app.main:app --debug --auto-reload --reload-dir app


.PHONY: test
test:
	poetry run pytest -s --verbose
