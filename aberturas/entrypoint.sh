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

# 4. Crear superusuario si no existe
echo "👤 Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin@akun.com', 'admin@akun.com', 'admin123')
    print('✅ Superusuario creado: admin@akun.com / admin123')
else:
    print('ℹ️  Superusuario ya existe')
"

# 5. Cargar datos básicos del catálogo
echo "📦 Cargando datos básicos del catálogo..."
python /app/create_basic_data.py

# 6. Cargar toda la parametría del sistema
echo "🚀 Cargando parametría del sistema..."
python /app/load_system_data.py

# 7. Cargar unidades de medida adicionales
echo "📏 Cargando unidades de medida..."
python /app/create_units.py

# 8. Cargar provincias, municipios y localidades
echo "🌍 Cargando datos geográficos..."
python manage.py loaddata fixtures/localidad_municipio_provincia.json 2>/dev/null || echo "ℹ️  Datos geográficos ya cargados"

# 9. Iniciar el servidor
echo "🌟 Iniciando servidor Django..."
exec "$@"