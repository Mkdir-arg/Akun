from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Analiza la estructura de la base de datos y las foreign keys'

    def handle(self, *args, **options):
        """Analiza la estructura de la base de datos y las foreign keys"""
        
        with connection.cursor() as cursor:
            # Obtener todas las tablas
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write("=== ANÁLISIS DE BASE DE DATOS AKUN ===\n")
            self.stdout.write(f"Total de tablas encontradas: {len(tables)}\n")
            
            # Listar todas las tablas
            self.stdout.write("TABLAS EN LA BASE DE DATOS:")
            self.stdout.write("-" * 50)
            for table in sorted(tables):
                self.stdout.write(f"- {table}")
            
            self.stdout.write("\n" + "="*80 + "\n")
            
            # Analizar foreign keys para cada tabla
            self.stdout.write("ANÁLISIS DE FOREIGN KEYS:")
            self.stdout.write("="*50)
            
            total_fks = 0
            problematic_fks = []
            
            for table in sorted(tables):
                self.stdout.write(f"\nTabla: {table}")
                self.stdout.write("-" * (len(table) + 7))
                
                # Obtener información de foreign keys
                cursor.execute(f"""
                    SELECT 
                        kcu.COLUMN_NAME,
                        kcu.CONSTRAINT_NAME,
                        kcu.REFERENCED_TABLE_NAME,
                        kcu.REFERENCED_COLUMN_NAME,
                        rc.UPDATE_RULE,
                        rc.DELETE_RULE
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    LEFT JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc 
                        ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME 
                        AND kcu.TABLE_SCHEMA = rc.CONSTRAINT_SCHEMA
                    WHERE kcu.TABLE_SCHEMA = 'akun' 
                    AND kcu.TABLE_NAME = '{table}' 
                    AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                """)
                
                fks = cursor.fetchall()
                
                if fks:
                    for fk in fks:
                        column, constraint, ref_table, ref_column, update_rule, delete_rule = fk
                        total_fks += 1
                        
                        self.stdout.write(f"  FK: {column} -> {ref_table}.{ref_column}")
                        self.stdout.write(f"      Constraint: {constraint}")
                        self.stdout.write(f"      ON UPDATE: {update_rule}, ON DELETE: {delete_rule}")
                        
                        # Verificar si la tabla referenciada existe
                        if ref_table not in tables:
                            problematic_fks.append({
                                'table': table,
                                'column': column,
                                'ref_table': ref_table,
                                'issue': 'Tabla referenciada no existe'
                            })
                            self.stdout.write(self.style.WARNING(f"      ⚠️  PROBLEMA: La tabla '{ref_table}' no existe!"))
                        else:
                            # Verificar si la columna referenciada existe
                            try:
                                cursor.execute(f"SHOW COLUMNS FROM {ref_table}")
                                ref_columns = [col[0] for col in cursor.fetchall()]
                                if ref_column not in ref_columns:
                                    problematic_fks.append({
                                        'table': table,
                                        'column': column,
                                        'ref_table': ref_table,
                                        'ref_column': ref_column,
                                        'issue': 'Columna referenciada no existe'
                                    })
                                    self.stdout.write(self.style.WARNING(f"      ⚠️  PROBLEMA: La columna '{ref_column}' no existe en '{ref_table}'!"))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"      Error verificando tabla {ref_table}: {e}"))
                        
                        self.stdout.write("")
                else:
                    self.stdout.write("  Sin foreign keys")
            
            self.stdout.write("\n" + "="*80 + "\n")
            
            # Resumen
            self.stdout.write("RESUMEN DEL ANÁLISIS:")
            self.stdout.write("="*30)
            self.stdout.write(f"Total de tablas: {len(tables)}")
            self.stdout.write(f"Total de foreign keys: {total_fks}")
            self.stdout.write(f"Foreign keys problemáticas: {len(problematic_fks)}")
            
            if problematic_fks:
                self.stdout.write(self.style.WARNING("\nPROBLEMAS ENCONTRADOS:"))
                self.stdout.write("-" * 30)
                for i, problem in enumerate(problematic_fks, 1):
                    self.stdout.write(f"{i}. Tabla '{problem['table']}', columna '{problem['column']}':")
                    self.stdout.write(f"   {problem['issue']}")
                    if 'ref_table' in problem:
                        self.stdout.write(f"   Referencia: {problem['ref_table']}.{problem.get('ref_column', 'N/A')}")
                    self.stdout.write("")
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ No se encontraron problemas con las foreign keys!"))
            
            # Analizar tablas que podrían necesitar relaciones
            self.stdout.write("\n" + "="*80 + "\n")
            self.stdout.write("ANÁLISIS DE POSIBLES RELACIONES FALTANTES:")
            self.stdout.write("="*50)
            
            # Buscar columnas que podrían ser foreign keys pero no están definidas como tal
            for table in sorted(tables):
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = cursor.fetchall()
                
                potential_fks = []
                for column in columns:
                    col_name = column[0]
                    col_type = column[1]
                    
                    # Buscar patrones comunes de foreign keys
                    if (col_name.endswith('_id') or 
                        col_name in ['customer_id', 'user_id', 'cliente_id', 'usuario_id', 'provincia_id', 'municipio_id', 'localidad_id'] or
                        col_name.startswith('id_')):
                        
                        # Verificar si ya es una foreign key
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                            WHERE TABLE_SCHEMA = 'akun' 
                            AND TABLE_NAME = '{table}' 
                            AND COLUMN_NAME = '{col_name}'
                            AND REFERENCED_TABLE_NAME IS NOT NULL
                        """)
                        
                        is_fk = cursor.fetchone()[0] > 0
                        
                        if not is_fk:
                            potential_fks.append(col_name)
                
                if potential_fks:
                    self.stdout.write(f"\nTabla '{table}' - Posibles FK faltantes:")
                    for col in potential_fks:
                        self.stdout.write(f"  - {col}")