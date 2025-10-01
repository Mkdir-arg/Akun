from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Analiza plantillas de forma simple'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("=== ANÁLISIS DE PLANTILLAS ===\n")
            
            # 1. Ver estructura de productos
            self.stdout.write("1. PRODUCTOS:")
            cursor.execute("SHOW COLUMNS FROM productos")
            columns = cursor.fetchall()
            self.stdout.write("Columnas:")
            for col in columns:
                self.stdout.write(f"  - {col[0]} ({col[1]})")
            
            cursor.execute("SELECT * FROM productos")
            productos = cursor.fetchall()
            self.stdout.write(f"\nTotal productos: {len(productos)}")
            for p in productos[:10]:
                self.stdout.write(f"  ID: {p[0]}, Desc: {p[4]}")
            
            # 2. Ver marcos
            self.stdout.write("\n2. MARCOS:")
            cursor.execute("SHOW COLUMNS FROM marco")
            columns = cursor.fetchall()
            self.stdout.write("Columnas:")
            for col in columns:
                self.stdout.write(f"  - {col[0]} ({col[1]})")
            
            cursor.execute("SELECT * FROM marco")
            marcos = cursor.fetchall()
            self.stdout.write(f"\nTotal marcos: {len(marcos)}")
            for m in marcos[:10]:
                self.stdout.write(f"  {m}")
            
            # 3. Ver hojas
            self.stdout.write("\n3. HOJAS:")
            cursor.execute("SELECT * FROM hoja")
            hojas = cursor.fetchall()
            self.stdout.write(f"Total hojas: {len(hojas)}")
            for h in hojas[:10]:
                self.stdout.write(f"  {h}")
            
            # 4. Ver interiores
            self.stdout.write("\n4. INTERIORES:")
            cursor.execute("SELECT * FROM interior")
            interiores = cursor.fetchall()
            self.stdout.write(f"Total interiores: {len(interiores)}")
            for i in interiores[:10]:
                self.stdout.write(f"  {i}")
            
            # 5. Plantillas Django existentes
            self.stdout.write("\n5. PLANTILLAS DJANGO:")
            cursor.execute("SELECT * FROM catalog_producttemplate")
            templates = cursor.fetchall()
            self.stdout.write(f"Total plantillas Django: {len(templates)}")
            for t in templates:
                self.stdout.write(f"  {t}")
            
            # 6. Resumen de tipos de productos
            self.stdout.write("\n6. TIPOS DE PRODUCTOS (por descripción):")
            cursor.execute("SELECT `descripción`, COUNT(*) as count FROM productos GROUP BY `descripción` ORDER BY count DESC")
            tipos = cursor.fetchall()
            for tipo in tipos:
                self.stdout.write(f"  {tipo[0]}: {tipo[1]} productos")
            
            # 7. Relación productos -> marcos
            self.stdout.write("\n7. RELACIÓN PRODUCTOS -> MARCOS:")
            cursor.execute("""
                SELECT p.`descripción`, COUNT(m.trial_id_1) as marcos_count
                FROM productos p
                LEFT JOIN marco m ON p.id = m.id_producto
                GROUP BY p.id, p.`descripción`
                HAVING marcos_count > 0
                ORDER BY marcos_count DESC
            """)
            relaciones = cursor.fetchall()
            for rel in relaciones:
                self.stdout.write(f"  {rel[0]}: {rel[1]} marcos")
            
            # 8. Cadena completa: producto -> marco -> hoja -> interior
            self.stdout.write("\n8. CADENA COMPLETA (primeros 10):")
            cursor.execute("""
                SELECT p.id, p.`descripción` as producto,
                       m.trial_id_1 as marco_id,
                       h.id as hoja_id,
                       i.id as interior_id
                FROM productos p
                JOIN marco m ON p.id = m.id_producto
                JOIN hoja h ON m.trial_id_1 = h.id_marco
                JOIN interior i ON h.id = i.id_hoja
                LIMIT 10
            """)
            cadenas = cursor.fetchall()
            for c in cadenas:
                self.stdout.write(f"  Producto {c[0]} ({c[1]}) -> Marco {c[2]} -> Hoja {c[3]} -> Interior {c[4]}")
            
            # 9. Componentes adicionales
            self.stdout.write("\n9. COMPONENTES ADICIONALES:")
            
            # Contravidrios
            cursor.execute("SELECT COUNT(*) FROM contravidrio")
            count = cursor.fetchone()[0]
            self.stdout.write(f"  Contravidrios: {count}")
            
            # Mosquiteros
            cursor.execute("SELECT COUNT(*) FROM mosquitero")
            count = cursor.fetchone()[0]
            self.stdout.write(f"  Mosquiteros: {count}")
            
            # Vidrios repartidos
            cursor.execute("SELECT COUNT(*) FROM vidrio_repartido")
            count = cursor.fetchone()[0]
            self.stdout.write(f"  Vidrios repartidos: {count}")
            
            # Cruces
            cursor.execute("SELECT COUNT(*) FROM cruces")
            count = cursor.fetchone()[0]
            self.stdout.write(f"  Cruces: {count}")
            
            self.stdout.write("\n=== CONCLUSIÓN ===")
            self.stdout.write("Estructura identificada:")
            self.stdout.write("PRODUCTO (base) -> MARCO -> HOJA -> INTERIOR")
            self.stdout.write("Componentes opcionales: contravidrio, mosquitero, vidrio_repartido, cruces")