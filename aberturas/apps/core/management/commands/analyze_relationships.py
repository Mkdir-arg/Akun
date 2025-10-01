from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Analiza las relaciones específicas entre marcos, hojas e interiores'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("=== ANÁLISIS DE RELACIONES ESPECÍFICAS ===\n")
            
            # 1. Relación PRODUCTO -> MARCO -> HOJA -> INTERIOR (cadena completa)
            self.stdout.write("1. CADENAS COMPLETAS PRODUCTO->MARCO->HOJA->INTERIOR:")
            self.stdout.write("-" * 70)
            cursor.execute("""
                SELECT 
                    p.`descripción` as producto,
                    m.`descripción` as marco,
                    h.`descripción` as hoja,
                    i.`descripción` as interior,
                    COUNT(*) as cantidad
                FROM productos p
                JOIN marco m ON p.id = m.`id producto`
                JOIN hoja h ON m.trial_id_1 = h.id_marco
                JOIN interior i ON h.id = i.id_hoja
                WHERE p.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY p.`descripción`, m.`descripción`, h.`descripción`, i.`descripción`
                ORDER BY p.`descripción`, cantidad DESC
                LIMIT 50
            """)
            
            relaciones = cursor.fetchall()
            current_producto = None
            
            for rel in relaciones:
                if rel[0] != current_producto:
                    current_producto = rel[0]
                    self.stdout.write(f"\n📦 {current_producto}:")
                
                self.stdout.write(f"  Marco: {rel[1]}")
                self.stdout.write(f"    └─ Hoja: {rel[2]}")
                self.stdout.write(f"       └─ Interior: {rel[3]} ({rel[4]} configs)")
                self.stdout.write("")
            
            # 2. Marcos específicos y sus hojas compatibles
            self.stdout.write("\n2. MARCOS Y SUS HOJAS COMPATIBLES:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT 
                    m.`descripción` as marco,
                    GROUP_CONCAT(DISTINCT h.`descripción` SEPARATOR ' | ') as hojas_compatibles,
                    COUNT(DISTINCT h.id) as total_hojas
                FROM marco m
                JOIN hoja h ON m.trial_id_1 = h.id_marco
                WHERE m.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY m.trial_id_1, m.`descripción`
                ORDER BY total_hojas DESC
                LIMIT 20
            """)
            
            marcos_hojas = cursor.fetchall()
            for mh in marcos_hojas:
                self.stdout.write(f"\n🔧 Marco: {mh[0]} ({mh[2]} hojas)")
                hojas = mh[1].split(' | ')
                for hoja in hojas[:5]:  # Mostrar solo las primeras 5
                    self.stdout.write(f"  ├─ {hoja}")
                if len(hojas) > 5:
                    self.stdout.write(f"  └─ ... y {len(hojas)-5} más")
            
            # 3. Hojas específicas y sus interiores compatibles
            self.stdout.write("\n\n3. HOJAS Y SUS INTERIORES COMPATIBLES:")
            self.stdout.write("-" * 50)
            cursor.execute("""
                SELECT 
                    h.`descripción` as hoja,
                    GROUP_CONCAT(DISTINCT i.`descripción` SEPARATOR ' | ') as interiores_compatibles,
                    COUNT(DISTINCT i.id) as total_interiores
                FROM hoja h
                JOIN interior i ON h.id = i.id_hoja
                WHERE h.`descripción` NOT LIKE '*TRIAL%'
                GROUP BY h.id, h.`descripción`
                ORDER BY total_interiores DESC
                LIMIT 20
            """)
            
            hojas_interiores = cursor.fetchall()
            for hi in hojas_interiores:
                self.stdout.write(f"\n🔨 Hoja: {hi[0]} ({hi[2]} interiores)")
                interiores = hi[1].split(' | ')
                for interior in interiores[:5]:
                    self.stdout.write(f"  ├─ {interior}")
                if len(interiores) > 5:
                    self.stdout.write(f"  └─ ... y {len(interiores)-5} más")
            
            # 4. Análisis por línea de producto
            self.stdout.write("\n\n4. RELACIONES POR LÍNEA DE PRODUCTO:")
            self.stdout.write("-" * 50)
            
            lineas_principales = ['A30', 'A40', 'Modena', 'Rotonda 640']
            
            for linea in lineas_principales:
                self.stdout.write(f"\n🏭 LÍNEA {linea}:")
                cursor.execute(f"""
                    SELECT 
                        p.`descripción` as producto,
                        m.`descripción` as marco,
                        h.`descripción` as hoja,
                        i.`descripción` as interior
                    FROM productos p
                    JOIN marco m ON p.id = m.`id producto`
                    JOIN hoja h ON m.trial_id_1 = h.id_marco
                    JOIN interior i ON h.id = i.id_hoja
                    WHERE p.`descripción` LIKE '%{linea}%'
                    AND p.`descripción` NOT LIKE '*TRIAL%'
                    LIMIT 10
                """)
                
                linea_data = cursor.fetchall()
                for ld in linea_data:
                    self.stdout.write(f"  {ld[0]}: {ld[1]} → {ld[2]} → {ld[3]}")
            
            # 5. Componentes opcionales y sus relaciones
            self.stdout.write("\n\n5. COMPONENTES OPCIONALES:")
            self.stdout.write("-" * 50)
            
            # Contravidrios
            cursor.execute("""
                SELECT 
                    i.`descripción` as interior_base,
                    COUNT(c.id) as contravidrios_disponibles
                FROM interior i
                LEFT JOIN contravidrio c ON i.id = c.`trial_id interior_2`
                GROUP BY i.id, i.`descripción`
                HAVING contravidrios_disponibles > 0
                ORDER BY contravidrios_disponibles DESC
                LIMIT 10
            """)
            
            contravidrios = cursor.fetchall()
            self.stdout.write("\n🔍 Interiores con Contravidrios:")
            for cv in contravidrios:
                self.stdout.write(f"  {cv[0]}: {cv[1]} contravidrios")
            
            # Mosquiteros
            cursor.execute("""
                SELECT 
                    h.`descripción` as hoja_base,
                    COUNT(m.id) as mosquiteros_disponibles
                FROM hoja h
                LEFT JOIN mosquitero m ON h.id = m.id_hoja
                GROUP BY h.id, h.`descripción`
                HAVING mosquiteros_disponibles > 0
                ORDER BY mosquiteros_disponibles DESC
                LIMIT 10
            """)
            
            mosquiteros = cursor.fetchall()
            self.stdout.write("\n🦟 Hojas con Mosquiteros:")
            for mq in mosquiteros:
                self.stdout.write(f"  {mq[0]}: {mq[1]} mosquiteros")
            
            # Vidrios repartidos
            cursor.execute("""
                SELECT 
                    i.`descripción` as interior_base,
                    COUNT(vr.id) as vidrios_repartidos
                FROM interior i
                LEFT JOIN vidrio_repartido vr ON i.id = vr.id_interior
                GROUP BY i.id, i.`descripción`
                HAVING vidrios_repartidos > 0
                ORDER BY vidrios_repartidos DESC
                LIMIT 10
            """)
            
            vidrios_repartidos = cursor.fetchall()
            self.stdout.write("\n🔲 Interiores con Vidrios Repartidos:")
            for vr in vidrios_repartidos:
                self.stdout.write(f"  {vr[0]}: {vr[1]} vidrios repartidos")
            
            self.stdout.write("\n" + "="*70)
            self.stdout.write("✅ ANÁLISIS DE RELACIONES COMPLETADO")
            self.stdout.write("Las opciones deben filtrarse según estas relaciones específicas")