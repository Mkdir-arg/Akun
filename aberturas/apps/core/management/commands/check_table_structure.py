from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Verifica la estructura de las tablas principales'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            tables = ['productos', 'marco', 'hoja', 'interior', 'contravidrio', 'mosquitero', 'vidrio_repartido']
            
            for table in tables:
                self.stdout.write(f"\n=== TABLA: {table} ===")
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = cursor.fetchall()
                for col in columns:
                    self.stdout.write(f"  {col[0]} ({col[1]})")
                
                # Mostrar algunos datos de ejemplo
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                self.stdout.write("Datos ejemplo:")
                for row in rows:
                    self.stdout.write(f"  {row}")
            
            # Verificar foreign keys específicas
            self.stdout.write("\n=== FOREIGN KEYS ===")
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = 'akun' 
                AND REFERENCED_TABLE_NAME IS NOT NULL
                AND TABLE_NAME IN ('marco', 'hoja', 'interior', 'contravidrio', 'mosquitero', 'vidrio_repartido')
                ORDER BY TABLE_NAME
            """)
            
            fks = cursor.fetchall()
            for fk in fks:
                self.stdout.write(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")