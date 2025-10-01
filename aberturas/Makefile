# Makefile para el Sistema de Aberturas

.PHONY: help build up down restart logs shell migrate fixtures backup clean

# Variables
COMPOSE_FILE = docker-compose.yml
SERVICE_WEB = web
SERVICE_DB = db

help: ## Mostrar ayuda
	@echo "Sistema de Aberturas - Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker
build: ## Construir contenedores
	docker compose -f $(COMPOSE_FILE) build

up: ## Levantar servicios
	docker compose -f $(COMPOSE_FILE) up -d

down: ## Bajar servicios
	docker compose -f $(COMPOSE_FILE) down

restart: ## Reiniciar servicios
	docker compose -f $(COMPOSE_FILE) restart

logs: ## Ver logs
	docker compose -f $(COMPOSE_FILE) logs -f $(SERVICE_WEB)

shell: ## Acceder al shell del contenedor web
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) bash

# Base de datos
migrate: ## Ejecutar migraciones
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py migrate

makemigrations: ## Crear migraciones
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py makemigrations

dbshell: ## Acceder al shell de la base de datos
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_DB) mysql -u root -p akun

# Fixtures y backups
fixtures: ## Crear fixtures del sistema
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python create_complete_fixtures.py

fixtures-load: ## Cargar fixtures del sistema
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py load_system_fixtures --complete

backup: ## Crear backup de la base de datos
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py backup_database --include-data

backup-structure: ## Crear backup solo estructura
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py backup_database

# Desarrollo
test: ## Ejecutar tests
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py test

collectstatic: ## Recopilar archivos estáticos
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py collectstatic --noinput

# Comandos personalizados
analyze-db: ## Analizar estructura de la base de datos
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py analyze_database

fix-db: ## Corregir problemas de la base de datos
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py fix_database_issues

test-templates: ## Probar sistema de plantillas
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) python manage.py test_presupuesto_plantilla

# Limpieza
clean: ## Limpiar contenedores y volúmenes
	docker compose -f $(COMPOSE_FILE) down -v
	docker system prune -f

clean-all: ## Limpieza completa (¡CUIDADO!)
	docker compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -af

# Desarrollo local (sin Docker)
dev-install: ## Instalar dependencias para desarrollo local
	pip install -r requirements.txt

dev-migrate: ## Migraciones en desarrollo local
	python manage.py migrate

dev-run: ## Ejecutar servidor de desarrollo local
	python manage.py runserver

dev-fixtures: ## Crear fixtures en desarrollo local
	python create_complete_fixtures.py

# Frontend
frontend-build: ## Construir CSS con Tailwind
	cd frontend && npm install && npm run build

frontend-watch: ## Modo watch para CSS
	cd frontend && npm run dev

# Información del sistema
status: ## Estado de los servicios
	docker compose -f $(COMPOSE_FILE) ps

info: ## Información del sistema
	@echo "Sistema de Aberturas"
	@echo "==================="
	@echo "Web: http://localhost:8090"
	@echo "Base de datos: localhost:13306"
	@echo "Redis: localhost:6380"
	@echo ""
	@echo "Usuarios por defecto:"
	@echo "- admin/admin (superusuario)"
	@echo ""
	@echo "Comandos útiles:"
	@echo "- make up          # Levantar sistema"
	@echo "- make fixtures    # Crear fixtures"
	@echo "- make backup      # Backup completo"
	@echo "- make logs        # Ver logs"

# Instalación completa
install: build up migrate fixtures info ## Instalación completa del sistema