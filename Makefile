.PHONY: help dev prod up down logs build clean test

help:
	@echo "Comandos disponíveis:"
	@echo "  make dev          - Rodar em modo desenvolvimento"
	@echo "  make prod         - Rodar em modo produção"
	@echo "  make up           - Subir containers (dev)"
	@echo "  make down         - Parar containers"
	@echo "  make logs         - Ver logs em tempo real"
	@echo "  make build        - Build das imagens"
	@echo "  make clean        - Limpar volumes e dados"
	@echo "  make test         - Rodar testes"
	@echo "  make shell-be     - Shell do backend"
	@echo "  make shell-fe     - Shell do frontend"

dev:
	docker-compose -f docker-compose.dev.yml up

prod:
	docker-compose up -d

up:
	docker-compose -f docker-compose.dev.yml up

down:
	docker-compose -f docker-compose.dev.yml down

logs:
	docker-compose -f docker-compose.dev.yml logs -f

logs-backend:
	docker-compose -f docker-compose.dev.yml logs -f backend

logs-frontend:
	docker-compose -f docker-compose.dev.yml logs -f frontend

build:
	docker-compose -f docker-compose.dev.yml build

build-prod:
	docker-compose build

clean:
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -a

test:
	docker-compose -f docker-compose.dev.yml exec backend pytest

shell-be:
	docker-compose -f docker-compose.dev.yml exec backend sh

shell-fe:
	docker-compose -f docker-compose.dev.yml exec frontend sh
