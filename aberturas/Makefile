.PHONY: help build up down logs migrate superuser shell tailwind lint format resetdb

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Construir contenedores
	docker-compose build

up: ## Levantar servicios
	docker-compose up -d

down: ## Bajar servicios
	docker-compose down

logs: ## Ver logs
	docker-compose logs -f web

migrate: ## Ejecutar migraciones
	docker-compose exec web python manage.py migrate

makemigrations: ## Crear migraciones
	docker-compose exec web python manage.py makemigrations

superuser: ## Crear superusuario
	docker-compose exec web python manage.py createsuperuser

shell: ## Abrir shell de Django
	docker-compose exec web python manage.py shell

tailwind: ## Compilar CSS con Tailwind
	docker-compose --profile frontend up node

tailwind-build: ## Compilar CSS para producción
	cd frontend && npm run build

lint: ## Ejecutar linters
	docker-compose exec web ruff check .
	docker-compose exec web black --check .
	docker-compose exec web isort --check-only .

format: ## Formatear código
	docker-compose exec web black .
	docker-compose exec web isort .

resetdb: ## Resetear base de datos (DESARROLLO)
	docker-compose down
	docker volume rm aberturas_mysql_data
	docker-compose up -d db
	sleep 10
	docker-compose up -d web
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py create_default_groups

install-dev: ## Instalar dependencias de desarrollo
	pip install -e ".[dev]"

seed: ## Crear datos de prueba
	docker-compose exec web python manage.py seed_catalog
	docker-compose exec web python manage.py seed_crm

perms: ## Asignar permisos por grupos
	docker-compose exec web python manage.py grant_domain_perms

setup: ## Setup inicial del proyecto
	cp .env.example .env
	docker-compose build
	docker-compose up -d
	sleep 15
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py create_default_groups
	@echo "Proyecto configurado. Crear superusuario con: make superuser"