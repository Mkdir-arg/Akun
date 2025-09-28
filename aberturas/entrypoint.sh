#!/bin/bash

# 1. Esperar a que la base de datos esté disponible
echo "🔄 Esperando a que la base de datos esté disponible..."
while ! python manage.py check --database default >/dev/null 2>&1; do
  echo "⏳ Base de datos no disponible, esperando..."
  sleep 3
done
echo "✅ Base de datos disponible!"

# 2. Verificar y crear migraciones si hay cambios
echo "🔍 Verificando migraciones pendientes..."
python manage.py makemigrations --dry-run --verbosity=0 | grep -q "No changes detected" || {
  echo "📝 Creando nuevas migraciones..."
  python manage.py makemigrations
}

# 3. Aplicar migraciones pendientes
echo "⚡ Aplicando migraciones..."
python manage.py migrate --verbosity=1

# 4. Ejecutar fixtures (configuración del sistema)
echo "🚀 Cargando datos iniciales del sistema..."
python manage.py setup_system

# 5. Iniciar el servidor
echo "🌟 Iniciando servidor Django..."
exec "$@"