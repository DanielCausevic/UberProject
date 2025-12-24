.PHONY: up down logs test lint

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

test:
	python -m pytest -q

lint:
	python -m ruff check .
