# AKUN - React + Django con Docker

## Configuración Inicial

1. **Copiar variables de entorno del backend:**
   ```bash
   cd aberturas
   copy .env.example .env
   ```

2. **Instalar dependencias del backend:**
   ```bash
   cd aberturas
   pip install -e .
   ```

## Ejecutar con Docker

### Opción 1: Script automático
```bash
start.bat
```

### Opción 2: Manual
```bash
docker-compose -f docker-compose.unified.yml up --build
```

## URLs de acceso

- **Frontend React:** http://localhost:3001
- **Backend Django:** http://localhost:8002
- **Admin Django:** http://localhost:8002/admin
- **MySQL:** localhost:3309
- **Redis:** localhost:6379

## Credenciales por defecto

Crear superusuario:
```bash
docker-compose -f docker-compose.unified.yml exec backend python manage.py createsuperuser
```

## Estructura del proyecto

```
├── src/                    # React Frontend
│   ├── App.tsx            # App principal
│   ├── Login.tsx          # Componente Login
│   └── Home.tsx           # Componente Home/Dashboard
├── aberturas/             # Django Backend
│   ├── apps/              # Apps Django
│   └── templates/         # Templates Django
└── docker-compose.unified.yml  # Docker Compose unificado
```

## Desarrollo

- **React:** Se recarga automáticamente en http://localhost:3001
- **Django:** Se recarga automáticamente en http://localhost:8002
- **Base de datos:** Persistente en volumen Docker