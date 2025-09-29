#!/bin/bash

# 1. Esperar a que la base de datos esté disponible
echo "🔄 Esperando a que la base de datos esté disponible..."
while ! python manage.py check --database default >/dev/null 2>&1; do
  echo "⏳ Base de datos no disponible, esperando..."
  sleep 3
done
echo "✅ Base de datos disponible!"

# 2. Crear migraciones automáticamente
echo "📝 Creando migraciones..."
python manage.py makemigrations

# 3. Aplicar migraciones
echo "⚡ Aplicando migraciones..."
python manage.py migrate

# 4. Ejecutar fixtures (configuración del sistema)
echo "🚀 Cargando datos iniciales del sistema..."
python manage.py setup_system 2>/dev/null || echo "⚠️  Datos ya existentes o error en carga inicial"

# 5. Iniciar el servidor
echo "🌟 Iniciando servidor Django..."
exec "$@"