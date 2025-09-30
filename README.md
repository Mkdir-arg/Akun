# Proyecto Akun - Versión Limpia

Proyecto Django minimalista con solo las funcionalidades esenciales:
- Login de usuarios
- Gestión de clientes (CRM)
- Plantillas de productos (Catalog)

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Crear superusuario:
```bash
python manage.py createsuperuser
```

5. Ejecutar servidor:
```bash
python manage.py runserver
```

## APIs Disponibles

- `/api/auth/login/` - Login
- `/api/auth/logout/` - Logout
- `/api/crm/clientes/` - CRUD de clientes
- `/api/catalog/templates/` - CRUD de plantillas
- `/api/catalog/attributes/` - CRUD de atributos
- `/api/catalog/options/` - CRUD de opciones