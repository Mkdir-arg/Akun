from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Extrae atributos y valores de las plantillas existentes'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("=== EXTRACCIÓN DE ATRIBUTOS DE PLANTILLAS ===\n")
            
            # 1. Extraer líneas disponibles
            self.stdout.write("1. LÍNEAS DISPONIBLES:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT * FROM líneas")
            lineas = cursor.fetchall()
            cursor.execute("SHOW COLUMNS FROM líneas")
            lineas_cols = [col[0] for col in cursor.fetchall()]
            
            lineas_dict = {}
            for linea in lineas:
                lineas_dict[linea[0]] = dict(zip(lineas_cols, linea))
                self.stdout.write(f"  ID {linea[0]}: {linea[1] if len(linea) > 1 else 'N/A'}")
            
            # 2. Extraer tipos de productos
            self.stdout.write("\n2. TIPOS DE PRODUCTOS:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT DISTINCT `id tipo`, `descripción` FROM productos WHERE `descripción` NOT LIKE '*TRIAL%' ORDER BY `descripción`")
            tipos = cursor.fetchall()
            for tipo in tipos:
                self.stdout.write(f"  Tipo {tipo[0]}: {tipo[1]}")
            
            # 3. Extraer marcos por producto
            self.stdout.write("\n3. MARCOS POR TIPO DE PRODUCTO:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT p.`descripción` as producto, m.`descripción` as marco, COUNT(*) as cantidad
                FROM productos p
                JOIN marco m ON p.id = m.`id producto`
                WHERE p.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY p.`descripción`, m.`descripción`
                ORDER BY p.`descripción`, cantidad DESC
            """)
            marcos_por_producto = cursor.fetchall()
            
            current_producto = None
            for item in marcos_por_producto:
                if item[0] != current_producto:
                    current_producto = item[0]
                    self.stdout.write(f"\n  📦 {current_producto}:")
                self.stdout.write(f"    - Marco: {item[1]} ({item[2]} configs)")
            
            # 4. Extraer tipos de hoja
            self.stdout.write("\n\n4. TIPOS DE HOJA:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT DISTINCT `descripción` FROM hoja WHERE `descripción` NOT LIKE '*TRIAL%' ORDER BY `descripción`")
            tipos_hoja = cursor.fetchall()
            for hoja in tipos_hoja:
                self.stdout.write(f"  - {hoja[0]}")
            
            # 5. Extraer tipos de interior
            self.stdout.write("\n5. TIPOS DE INTERIOR:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT DISTINCT `descripción` FROM interior WHERE `descripción` NOT LIKE '*TRIAL%' ORDER BY `descripción`")
            tipos_interior = cursor.fetchall()
            for interior in tipos_interior:
                self.stdout.write(f"  - {interior[0]}")
            
            # 6. Extraer accesorios disponibles
            self.stdout.write("\n6. ACCESORIOS DISPONIBLES:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT a.descripcion, ta.descripcion as tipo
                FROM accesorios a
                LEFT JOIN tipo_accesorios ta ON a.tipo = ta.id
                LIMIT 20
            """)
            accesorios = cursor.fetchall()
            for acc in accesorios:
                self.stdout.write(f"  - {acc[0]} (Tipo: {acc[1] or 'N/A'})")
            
            # 7. Extraer vidrios disponibles
            self.stdout.write("\n7. VIDRIOS DISPONIBLES:")
            self.stdout.write("-" * 50)
            cursor.execute("SELECT DISTINCT descripcion FROM vidrios LIMIT 15")
            vidrios = cursor.fetchall()
            for vidrio in vidrios:
                self.stdout.write(f"  - {vidrio[0]}")
            
            # 8. Extraer perfiles por línea
            self.stdout.write("\n8. PERFILES POR LÍNEA:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT l.descripcion as linea, COUNT(p.id) as cantidad_perfiles
                FROM líneas l
                LEFT JOIN perfiles p ON l.id = p.`trial_id línea_2`
                GROUP BY l.id, l.descripcion
                ORDER BY cantidad_perfiles DESC
            """)
            perfiles_linea = cursor.fetchall()
            for pl in perfiles_linea:
                self.stdout.write(f"  - Línea {pl[0]}: {pl[1]} perfiles")
            
            # 9. Generar estructura de plantillas
            self.stdout.write("\n\n" + "="*80)
            self.stdout.write("ESTRUCTURA DE PLANTILLAS IDENTIFICADA:")
            self.stdout.write("="*80)
            
            # Agrupar por categorías principales
            categorias = {
                'VENTANA': [],
                'PUERTA': [],
                'PAÑO_FIJO': [],
                'ACCESORIO': []
            }
            
            for tipo in tipos:
                desc = tipo[1].upper()
                if 'VENTANA' in desc:
                    categorias['VENTANA'].append(tipo[1])
                elif 'PUERTA' in desc:
                    categorias['PUERTA'].append(tipo[1])
                elif 'PAÑO' in desc or 'FIJO' in desc:
                    categorias['PAÑO_FIJO'].append(tipo[1])
                else:
                    categorias['ACCESORIO'].append(tipo[1])
            
            for categoria, productos in categorias.items():
                if productos:
                    self.stdout.write(f"\n📋 PLANTILLA: {categoria}")
                    self.stdout.write("   ATRIBUTOS:")
                    self.stdout.write("   - línea: SELECT")
                    self.stdout.write("   - tipo_apertura: SELECT") 
                    self.stdout.write("   - marco: SELECT")
                    self.stdout.write("   - hoja: SELECT")
                    self.stdout.write("   - interior: SELECT")
                    self.stdout.write("   - dimensiones: DIMENSIONS_MM")
                    self.stdout.write("   - cantidad: QUANTITY")
                    
                    if categoria in ['VENTANA', 'PUERTA']:
                        self.stdout.write("   - contravidrio: BOOLEAN")
                        self.stdout.write("   - mosquitero: BOOLEAN")
                        self.stdout.write("   - vidrio_repartido: BOOLEAN")
                        self.stdout.write("   - cruces: BOOLEAN")
                    
                    self.stdout.write("   VALORES:")
                    for producto in productos[:5]:  # Mostrar solo los primeros 5
                        self.stdout.write(f"   - {producto}")
                    if len(productos) > 5:
                        self.stdout.write(f"   ... y {len(productos)-5} más")
            
            self.stdout.write(f"\n✅ Análisis completado. Plantillas identificadas: {len([p for productos in categorias.values() for p in productos])}")