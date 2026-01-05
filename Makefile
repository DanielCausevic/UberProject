.PHONY: up down logs test lint k8s-up k8s-down k8s-logs

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

k8s-up:
	kubectl apply -f k8s/

k8s-down:
	kubectl delete -f k8s/

k8s-logs:
	kubectl logs -f deployment/gateway

test:
	python -m pytest -q

lint:
	python -m ruff check .
