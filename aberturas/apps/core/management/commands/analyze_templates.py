from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Analiza todas las tablas para identificar plantillas y sus relaciones'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("=== ANÁLISIS DE PLANTILLAS Y DATOS ===\n")
            
            # 1. Analizar tabla productos (base de plantillas)
            self.stdout.write("1. PRODUCTOS (Base de plantillas):")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM productos LIMIT 10")
            productos = cursor.fetchall()
            if productos:
                # Obtener nombres de columnas
                cursor.execute("SHOW COLUMNS FROM productos")
                columns = [col[0] for col in cursor.fetchall()]
                self.stdout.write(f"Columnas: {', '.join(columns)}")
                for producto in productos:
                    self.stdout.write(f"  {dict(zip(columns, producto))}")
            else:
                self.stdout.write("  Sin datos")
            
            # 2. Analizar modelos y modelos_productos
            self.stdout.write("\n2. MODELOS:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM modelos")
            modelos = cursor.fetchall()
            if modelos:
                cursor.execute("SHOW COLUMNS FROM modelos")
                columns = [col[0] for col in cursor.fetchall()]
                self.stdout.write(f"Columnas: {', '.join(columns)}")
                for modelo in modelos:
                    self.stdout.write(f"  {dict(zip(columns, modelo))}")
            
            self.stdout.write("\n3. MODELOS_PRODUCTOS:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM modelos_productos")
            modelos_prod = cursor.fetchall()
            if modelos_prod:
                cursor.execute("SHOW COLUMNS FROM modelos_productos")
                columns = [col[0] for col in cursor.fetchall()]
                self.stdout.write(f"Columnas: {', '.join(columns)}")
                for mp in modelos_prod:
                    self.stdout.write(f"  {dict(zip(columns, mp))}")
            
            # 3. Analizar estructura jerárquica: productos -> marco -> hoja -> interior
            self.stdout.write("\n4. ESTRUCTURA JERÁRQUICA:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT p.id as producto_id, p.descripcion as producto,
                       m.trial_id_1 as marco_id, m.descripcion as marco,
                       h.id as hoja_id, h.descripcion as hoja,
                       i.id as interior_id, i.descripcion as interior
                FROM productos p
                LEFT JOIN marco m ON p.id = m.id_producto
                LEFT JOIN hoja h ON m.trial_id_1 = h.id_marco
                LEFT JOIN interior i ON h.id = i.id_hoja
                LIMIT 20
            """)
            jerarquia = cursor.fetchall()
            for j in jerarquia:
                self.stdout.write(f"  Producto: {j[1]} -> Marco: {j[3]} -> Hoja: {j[5]} -> Interior: {j[7]}")
            
            # 4. Analizar tipos y opciones
            self.stdout.write("\n5. TIPOS DE ACCESORIOS:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM tipo_accesorios")
            tipos_acc = cursor.fetchall()
            if tipos_acc:
                cursor.execute("SHOW COLUMNS FROM tipo_accesorios")
                columns = [col[0] for col in cursor.fetchall()]
                for tipo in tipos_acc:
                    self.stdout.write(f"  {dict(zip(columns, tipo))}")
            
            self.stdout.write("\n6. TIPOS DE INTERIORES:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM tipo_interiores")
            tipos_int = cursor.fetchall()
            if tipos_int:
                cursor.execute("SHOW COLUMNS FROM tipo_interiores")
                columns = [col[0] for col in cursor.fetchall()]
                for tipo in tipos_int:
                    self.stdout.write(f"  {dict(zip(columns, tipo))}")
            
            # 5. Analizar opciones disponibles
            self.stdout.write("\n7. OPCIONES:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM opciones LIMIT 10")
            opciones = cursor.fetchall()
            if opciones:
                cursor.execute("SHOW COLUMNS FROM opciones")
                columns = [col[0] for col in cursor.fetchall()]
                for opcion in opciones:
                    self.stdout.write(f"  {dict(zip(columns, opcion))}")
            
            # 6. Analizar accesorios
            self.stdout.write("\n8. ACCESORIOS:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT a.*, ta.descripcion as tipo_desc FROM accesorios a LEFT JOIN tipo_accesorios ta ON a.tipo = ta.id LIMIT 10")
            accesorios = cursor.fetchall()
            if accesorios:
                cursor.execute("SHOW COLUMNS FROM accesorios")
                acc_columns = [col[0] for col in cursor.fetchall()]
                acc_columns.append('tipo_desc')
                for acc in accesorios:
                    self.stdout.write(f"  {dict(zip(acc_columns, acc))}")
            
            # 7. Analizar vidrios
            self.stdout.write("\n9. VIDRIOS:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM vidrios LIMIT 10")
            vidrios = cursor.fetchall()
            if vidrios:
                cursor.execute("SHOW COLUMNS FROM vidrios")
                columns = [col[0] for col in cursor.fetchall()]
                for vidrio in vidrios:
                    self.stdout.write(f"  {dict(zip(columns, vidrio))}")
            
            # 8. Analizar perfiles
            self.stdout.write("\n10. PERFILES:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT p.*, l.descripcion as linea_desc FROM perfiles p LEFT JOIN líneas l ON p.trial_id_línea_2 = l.id LIMIT 10")
            perfiles = cursor.fetchall()
            if perfiles:
                cursor.execute("SHOW COLUMNS FROM perfiles")
                perf_columns = [col[0] for col in cursor.fetchall()]
                perf_columns.append('linea_desc')
                for perfil in perfiles:
                    self.stdout.write(f"  {dict(zip(perf_columns, perfil))}")
            
            # 9. Contar registros por tabla clave
            self.stdout.write("\n11. RESUMEN DE REGISTROS:")
            self.stdout.write("-" * 50)
            tablas_clave = ['productos', 'modelos', 'modelos_productos', 'marco', 'hoja', 'interior', 
                           'accesorios', 'vidrios', 'perfiles', 'opciones', 'tipo_accesorios', 'tipo_interiores']
            
            for tabla in tablas_clave:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                self.stdout.write(f"  {tabla}: {count} registros")
            
            # 10. Identificar plantillas basadas en productos únicos
            self.stdout.write("\n12. PLANTILLAS IDENTIFICADAS:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT DISTINCT p.descripcion, COUNT(m.trial_id_1) as marcos_count
                FROM productos p
                LEFT JOIN marco m ON p.id = m.id_producto
                GROUP BY p.id, p.descripcion
                ORDER BY p.descripcion
            """)
            plantillas = cursor.fetchall()
            for plantilla in plantillas:
                self.stdout.write(f"  Plantilla: {plantilla[0]} ({plantilla[1]} marcos)")