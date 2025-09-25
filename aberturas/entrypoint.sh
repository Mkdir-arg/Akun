#!/bin/bash

# Esperar a que la base de datos esté disponible
echo "Esperando a que la base de datos esté disponible..."
while ! python manage.py check --database default; do
  echo "Base de datos no disponible, esperando..."
  sleep 2
done

echo "Base de datos disponible!"

# Siempre crear migraciones para detectar cambios
echo "Verificando y creando migraciones..."
python manage.py makemigrations

# Ejecutar todas las migraciones pendientes
echo "Aplicando migraciones..."
python manage.py migrate

# Crear grupos por defecto
echo "Creando grupos por defecto..."
python manage.py create_default_groups || echo "Grupos ya existen, continuando..."

# Iniciar el servidor
echo "Iniciando servidor Django..."
exec "$@"