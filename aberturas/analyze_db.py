#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aberturas.settings.dev')
django.setup()

from django.db import connection

def analyze_database():
    """Analiza la estructura de la base de datos y las foreign keys"""
    
    with connection.cursor() as cursor:
        # Obtener todas las tablas
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("=== ANÁLISIS DE BASE DE DATOS AKUN ===\n")
        print(f"Total de tablas encontradas: {len(tables)}\n")
        
        # Listar todas las tablas
        print("TABLAS EN LA BASE DE DATOS:")
        print("-" * 50)
        for table in sorted(tables):
            print(f"- {table}")
        
        print("\n" + "="*80 + "\n")
        
        # Analizar foreign keys para cada tabla
        print("ANÁLISIS DE FOREIGN KEYS:")
        print("="*50)
        
        total_fks = 0
        problematic_fks = []
        
        for table in sorted(tables):
            print(f"\nTabla: {table}")
            print("-" * (len(table) + 7))
            
            # Obtener información de foreign keys
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    CONSTRAINT_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME,
                    UPDATE_RULE,
                    DELETE_RULE
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = 'akun' 
                AND TABLE_NAME = '{table}' 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            fks = cursor.fetchall()
            
            if fks:
                for fk in fks:
                    column, constraint, ref_table, ref_column, update_rule, delete_rule = fk
                    total_fks += 1
                    
                    print(f"  FK: {column} -> {ref_table}.{ref_column}")
                    print(f"      Constraint: {constraint}")
                    print(f"      ON UPDATE: {update_rule}, ON DELETE: {delete_rule}")
                    
                    # Verificar si la tabla referenciada existe
                    if ref_table not in tables:
                        problematic_fks.append({
                            'table': table,
                            'column': column,
                            'ref_table': ref_table,
                            'issue': 'Tabla referenciada no existe'
                        })
                        print(f"      ⚠️  PROBLEMA: La tabla '{ref_table}' no existe!")
                    
                    # Verificar si la columna referenciada existe
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
                        print(f"      ⚠️  PROBLEMA: La columna '{ref_column}' no existe en '{ref_table}'!")
                    
                    print()
            else:
                print("  Sin foreign keys")
        
        print("\n" + "="*80 + "\n")
        
        # Resumen
        print("RESUMEN DEL ANÁLISIS:")
        print("="*30)
        print(f"Total de tablas: {len(tables)}")
        print(f"Total de foreign keys: {total_fks}")
        print(f"Foreign keys problemáticas: {len(problematic_fks)}")
        
        if problematic_fks:
            print("\nPROBLEMAS ENCONTRADOS:")
            print("-" * 30)
            for i, problem in enumerate(problematic_fks, 1):
                print(f"{i}. Tabla '{problem['table']}', columna '{problem['column']}':")
                print(f"   {problem['issue']}")
                if 'ref_table' in problem:
                    print(f"   Referencia: {problem['ref_table']}.{problem.get('ref_column', 'N/A')}")
                print()
        else:
            print("\n✅ No se encontraron problemas con las foreign keys!")
        
        # Analizar tablas que podrían necesitar relaciones
        print("\n" + "="*80 + "\n")
        print("ANÁLISIS DE POSIBLES RELACIONES FALTANTES:")
        print("="*50)
        
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
                print(f"\nTabla '{table}' - Posibles FK faltantes:")
                for col in potential_fks:
                    print(f"  - {col}")

if __name__ == "__main__":
    analyze_database()