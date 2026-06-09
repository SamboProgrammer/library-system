.PHONY: help install test lint build up down seed logs clean

help:
	@echo "Library Management System — DevOps Commands"
	@echo ""
	@echo "  install     Install Python dependencies"
	@echo "  test        Run full test suite with coverage"
	@echo "  lint        Run flake8 linter"
	@echo "  security    Run security scans (bandit + safety)"
	@echo "  build       Build Docker image"
	@echo "  up          Start full stack (app + DB + monitoring)"
	@echo "  down        Stop all services"
	@echo "  seed        Seed database with sample data"
	@echo "  logs        Tail application logs"
	@echo "  shell       Open app container shell"
	@echo "  clean       Remove all containers and volumes"
	@echo ""
	@echo "URLs when running:"
	@echo "  App:        http://localhost:5000"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3000  (admin/admin)"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	flake8 app/ --max-line-length=100 --ignore=E501

security:
	bandit -r app/ -ll
	safety check -r requirements.txt

build:
	docker build -t library-system:latest --target production .

build-dev:
	docker build -t library-system:dev --target builder .

up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "Stack is up! Visit http://localhost:5000/health"

down:
	docker-compose down

seed:
	python scripts/seed_db.py

logs:
	docker-compose logs -f app

shell:
	docker-compose exec app /bin/sh

clean:
	docker-compose down -v --remove-orphans
	docker image rm library-system:latest 2>/dev/null || true

# Docker image tagging for CI
tag:
	docker tag library-system:latest ghcr.io/$(GITHUB_REPO)/library-system:$(TAG)
	docker push ghcr.io/$(GITHUB_REPO)/library-system:$(TAG)

# Kubernetes operations
k8s-apply:
	kubectl apply -f k8s/ --namespace=library

k8s-status:
	kubectl get all --namespace=library

k8s-rollback:
	kubectl rollout undo deployment/library-app --namespace=library
