# Sistema de Gestión para Empresa de Aberturas

Sistema de gestión integral para empresas dedicadas a la fabricación y venta de aberturas (ventanas y puertas), desarrollado con Django 4.2 LTS, MySQL, Redis, HTMX, Tailwind CSS y DaisyUI.

## 🚀 Características

- **Backend**: Django 4.2 LTS con Python 3.12
- **Base de datos**: MySQL 8.0 con charset utf8mb4
- **Cache/Sesiones**: Redis 7
- **Frontend**: Django Templates + HTMX + Tailwind CSS + DaisyUI
- **Contenedores**: Docker + Docker Compose
- **Calidad de código**: Black, isort, Ruff, pre-commit hooks
- **Timezone**: America/Argentina/Buenos_Aires
- **Idioma**: Español (Argentina)

### Módulos Implementados (Etapa 2)

- **CRM**: Gestión de clientes y direcciones
- **Catálogo**: Productos, categorías, UoM, impuestos y listas de precios
- **Precios por área**: Sistema de cálculo de precios por m² para aberturas
- **Permisos por grupos**: Control de acceso granular por roles

## 📋 Requisitos Previos

- Docker y Docker Compose
- Make (opcional, para comandos simplificados)
- Node.js 20+ (para desarrollo de frontend)

## 🛠️ Instalación y Configuración

### 1. Clonar y configurar el proyecto

```bash
# Clonar el repositorio
git clone <repository-url>
cd aberturas

# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus configuraciones si es necesario
```

### 2. Levantar el proyecto con Docker

```bash
# Opción A: Usando Make (recomendado)
make setup

# Opción B: Comandos manuales
docker-compose build
docker-compose up -d
# Esperar que los servicios estén listos (~15 segundos)
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_default_groups
```

### 3. Crear superusuario

```bash
# Con Make
make superuser

# Manual
docker-compose exec web python manage.py createsuperuser
```

### 4. Compilar CSS (Tailwind)

```bash
# Con Make
make tailwind

# Manual
docker-compose --profile frontend up node
```

## 🌐 Acceso a la Aplicación

- **Aplicación principal**: http://localhost:8000
- **Panel de administración**: http://localhost:8000/admin/
- **Health check**: http://localhost:8000/health/
- **MailHog** (opcional): http://localhost:8025

## 📁 Estructura del Proyecto

```
aberturas/
├── aberturas/                 # Configuración principal de Django
│   ├── settings/             # Settings por entorno (base, dev, prod)
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # WSGI para producción
│   └── asgi.py              # ASGI para producción
├── apps/                     # Aplicaciones Django
│   ├── core/                # Utilidades, constantes, mixins
│   ├── accounts/            # Usuarios y autenticación
│   └── ui/                  # Templates y vistas de interfaz
├── templates/               # Templates base
├── static/                  # Archivos estáticos
├── frontend/                # Configuración de Node.js/Tailwind
├── docker-compose.yml       # Configuración de servicios
├── Dockerfile              # Imagen de la aplicación
├── Makefile                # Comandos útiles
└── pyproject.toml          # Dependencias Python
```

## 🔧 Comandos Útiles

### Con Make

```bash
make help          # Ver todos los comandos disponibles
make up            # Levantar servicios
make down          # Bajar servicios
make logs          # Ver logs de la aplicación
make migrate       # Ejecutar migraciones
make shell         # Abrir shell de Django
make tailwind      # Compilar CSS en modo watch
make lint          # Ejecutar linters
make format        # Formatear código
make resetdb       # Resetear base de datos (DESARROLLO)
make seed          # Crear datos de prueba (catalog + crm)
make perms         # Asignar permisos por grupos
```

### Comandos Docker directos

```bash
# Ver logs
docker-compose logs -f web

# Ejecutar comandos Django
docker-compose exec web python manage.py <comando>

# Acceder al shell del contenedor
docker-compose exec web bash

# Reiniciar servicios
docker-compose restart web
```

## 🎨 Desarrollo Frontend

### Compilar CSS

```bash
# Modo desarrollo (watch)
cd frontend
npm install
npm run dev

# Modo producción
npm run build
```

### Personalizar estilos

- Editar `frontend/src/styles.css` para estilos personalizados
- Modificar `frontend/tailwind.config.js` para configuración de Tailwind
- Los estilos compilados se generan en `static/build/styles.css`

## 🧪 Calidad de Código

### Configurar pre-commit hooks

```bash
# Instalar dependencias de desarrollo
make install-dev

# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

### Linting y formateo

```bash
# Formatear código
make format

# Verificar código
make lint
```

## 🗄️ Base de Datos

### Migraciones

```bash
# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
make migrate
```

### Resetear base de datos (DESARROLLO)

```bash
make resetdb
```

## 👥 Usuarios y Grupos

El sistema crea automáticamente los siguientes grupos:

- **Administración**: Acceso completo al sistema
- **Ventas**: Gestión de pedidos y clientes
- **Deposito**: Control de inventario
- **Produccion**: Seguimiento de fabricación

## 🧪 Pruebas Manuales (Etapa 2)

### 1. Configuración inicial
```bash
# Ejecutar migraciones
make migrate

# Crear datos de prueba
make seed

# Asignar permisos
make perms
```

### 2. Pruebas de funcionalidad

1. **Productos**: 
   - Ir a `/catalog/products/`
   - Filtrar por categoría, material, tipo de apertura
   - Crear/editar productos con diferentes métodos de precio
   - Verificar cálculo de precios por área vs precio fijo

2. **Listas de Precios**:
   - Ir a `/catalog/pricelists/`
   - Crear lista de precios y reglas específicas
   - Probar endpoint de preview: `/catalog/pricing/preview/`

3. **Clientes**:
   - Ir a `/crm/customers/`
   - Crear clientes persona/empresa
   - Agregar direcciones de facturación/envío
   - Verificar generación automática de códigos

4. **Permisos**:
   - Crear usuarios en diferentes grupos
   - Verificar accesos según rol (Ventas, Depósito, Producción)

5. **HTMX**:
   - Verificar filtros sin recarga de página
   - Probar ordenamiento por columnas con Hyperscript
   - Comprobar paginación AJAX

## 🚀 Despliegue en Producción

### Variables de entorno

Configurar las siguientes variables para producción:

```bash
DJANGO_SETTINGS_MODULE=aberturas.settings.prod
DEBUG=False
SECRET_KEY=<clave-secreta-segura>
ALLOWED_HOSTS=tu-dominio.com
# ... otras variables según necesidad
```

### Comandos de producción

```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Usar Gunicorn en lugar del servidor de desarrollo
# (configurar en docker-compose.prod.yml)
```

## 🔍 Monitoreo

- **Health check**: `GET /health/` retorna `{"status": "ok"}`
- **Logs**: Configurados para salida JSON en producción
- **Métricas**: Preparado para integración con herramientas de monitoreo

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, crear un issue en el repositorio del proyecto.

---

**Versión**: 0.1.0  
**Última actualización**: Diciembre 2024