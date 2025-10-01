from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Analiza las relaciones reales entre componentes'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("=== RELACIONES REALES ENTRE COMPONENTES ===\n")
            
            # 1. Cadena completa: PRODUCTO -> MARCO -> HOJA -> INTERIOR
            self.stdout.write("1. CADENAS COMPLETAS (con nombres correctos):")
            self.stdout.write("-" * 60)
            cursor.execute("""
                SELECT 
                    p.`descripción` as producto,
                    m.`descripción` as marco,
                    h.`descripción` as hoja,
                    i.`descripción` as interior
                FROM productos p
                JOIN marco m ON p.id = m.`id producto`
                JOIN hoja h ON m.trial_id_1 = h.`id marco`
                JOIN interior i ON h.id = i.`id hoja`
                WHERE p.`descripción` NOT LIKE '*TRIAL%'
                AND m.`descripción` NOT LIKE '*TRIAL%'
                AND h.`descripción` NOT LIKE '*TRIAL%'
                AND i.`descripción` NOT LIKE '*TRIAL%'
                ORDER BY p.`descripción`
                LIMIT 30
            """)
            
            cadenas = cursor.fetchall()
            current_producto = None
            
            for cadena in cadenas:
                if cadena[0] != current_producto:
                    current_producto = cadena[0]
                    self.stdout.write(f"\n📦 {current_producto}:")
                
                self.stdout.write(f"  {cadena[1]} → {cadena[2]} → {cadena[3]}")
            
            # 2. Marcos específicos y sus hojas válidas
            self.stdout.write("\n\n2. MARCOS Y SUS HOJAS VÁLIDAS:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT 
                    m.`descripción` as marco,
                    COUNT(DISTINCT h.id) as total_hojas,
                    GROUP_CONCAT(DISTINCT h.`descripción` ORDER BY h.`descripción` SEPARATOR ' | ') as hojas
                FROM marco m
                JOIN hoja h ON m.trial_id_1 = h.`id marco`
                WHERE m.`descripción` NOT LIKE '*TRIAL%'
                AND h.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY m.trial_id_1, m.`descripción`
                HAVING total_hojas > 0
                ORDER BY total_hojas DESC
                LIMIT 15
            """)
            
            marcos_hojas = cursor.fetchall()
            for mh in marcos_hojas:
                self.stdout.write(f"\n🔧 Marco: {mh[0]} ({mh[1]} hojas)")
                if mh[2]:
                    hojas = mh[2].split(' | ')
                    for hoja in hojas[:3]:
                        self.stdout.write(f"  ├─ {hoja}")
                    if len(hojas) > 3:
                        self.stdout.write(f"  └─ ... y {len(hojas)-3} más")
            
            # 3. Hojas específicas y sus interiores válidos
            self.stdout.write("\n\n3. HOJAS Y SUS INTERIORES VÁLIDOS:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT 
                    h.`descripción` as hoja,
                    COUNT(DISTINCT i.id) as total_interiores,
                    GROUP_CONCAT(DISTINCT i.`descripción` ORDER BY i.`descripción` SEPARATOR ' | ') as interiores
                FROM hoja h
                JOIN interior i ON h.id = i.`id hoja`
                WHERE h.`descripción` NOT LIKE '*TRIAL%'
                AND i.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY h.id, h.`descripción`
                HAVING total_interiores > 0
                ORDER BY total_interiores DESC
                LIMIT 15
            """)
            
            hojas_interiores = cursor.fetchall()
            for hi in hojas_interiores:
                self.stdout.write(f"\n🔨 Hoja: {hi[0]} ({hi[1]} interiores)")
                if hi[2]:
                    interiores = hi[2].split(' | ')
                    for interior in interiores[:3]:
                        self.stdout.write(f"  ├─ {interior}")
                    if len(interiores) > 3:
                        self.stdout.write(f"  └─ ... y {len(interiores)-3} más")
            
            # 4. Componentes opcionales por interior
            self.stdout.write("\n\n4. COMPONENTES OPCIONALES POR INTERIOR:")
            self.stdout.write("-" * 50)
            
            cursor.execute("""
                SELECT 
                    i.`descripción` as interior,
                    COUNT(c.id) as contravidrios,
                    COUNT(vr.id) as vidrios_repartidos
                FROM interior i
                LEFT JOIN contravidrio c ON i.id = c.`trial_id interior_2`
                LEFT JOIN vidrio_repartido vr ON i.id = vr.`id interior`
                WHERE i.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY i.id, i.`descripción`
                HAVING contravidrios > 0 OR vidrios_repartidos > 0
                ORDER BY contravidrios DESC, vidrios_repartidos DESC
                LIMIT 15
            """)
            
            componentes = cursor.fetchall()
            for comp in componentes:
                opciones = []
                if comp[1] > 0:
                    opciones.append(f"Contravidrios: {comp[1]}")
                if comp[2] > 0:
                    opciones.append(f"Vidrios repartidos: {comp[2]}")
                
                self.stdout.write(f"🔍 Interior: {comp[0]}")
                self.stdout.write(f"  └─ {', '.join(opciones)}")
            
            # 5. Mosquiteros por hoja
            self.stdout.write("\n\n5. MOSQUITEROS POR HOJA:")
            self.stdout.write("-" * 30)
            cursor.execute("""
                SELECT 
                    h.`descripción` as hoja,
                    COUNT(m.id) as mosquiteros
                FROM hoja h
                LEFT JOIN mosquitero m ON h.id = m.`id hoja`
                WHERE h.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY h.id, h.`descripción`
                HAVING mosquiteros > 0
                ORDER BY mosquiteros DESC
                LIMIT 10
            """)
            
            mosquiteros = cursor.fetchall()
            for mq in mosquiteros:
                self.stdout.write(f"🦟 {mq[0]}: {mq[1]} mosquiteros")
            
            # 6. Ejemplo de filtrado por línea
            self.stdout.write("\n\n6. EJEMPLO: VENTANA A30 - OPCIONES VÁLIDAS:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT DISTINCT
                    m.`descripción` as marco,
                    h.`descripción` as hoja,
                    i.`descripción` as interior
                FROM productos p
                JOIN marco m ON p.id = m.`id producto`
                JOIN hoja h ON m.trial_id_1 = h.`id marco`
                JOIN interior i ON h.id = i.`id hoja`
                WHERE p.`descripción` LIKE '%A30%'
                AND p.`descripción` LIKE '%Ventana%'
                AND m.`descripción` NOT LIKE '*TRIAL%'
                AND h.`descripción` NOT LIKE '*TRIAL%'
                AND i.`descripción` NOT LIKE '*TRIAL%'
                ORDER BY m.`descripción`, h.`descripción`, i.`descripción`
            """)
            
            a30_opciones = cursor.fetchall()
            current_marco = None
            current_hoja = None
            
            for opcion in a30_opciones:
                if opcion[0] != current_marco:
                    current_marco = opcion[0]
                    self.stdout.write(f"\n🔧 Marco: {current_marco}")
                    current_hoja = None
                
                if opcion[1] != current_hoja:
                    current_hoja = opcion[1]
                    self.stdout.write(f"  🔨 Hoja: {current_hoja}")
                
                self.stdout.write(f"    🔍 Interior: {opcion[2]}")
            
            self.stdout.write("\n" + "="*70)
            self.stdout.write("✅ ANÁLISIS COMPLETADO")
            self.stdout.write("IMPORTANTE: Los atributos deben filtrarse según estas relaciones específicas")
            self.stdout.write("No todos los marcos van con todas las hojas, ni todas las hojas con todos los interiores")