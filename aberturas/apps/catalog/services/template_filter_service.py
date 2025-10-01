from django.db import connection
from typing import Dict, List, Optional
from django.core.cache import cache

class TemplateFilterService:
    """Servicio para filtrado dinámico de opciones de plantillas"""
    
    CACHE_TIMEOUT = 3600  # 1 hora
    
    @classmethod
    def get_lineas(cls) -> List[Dict]:
        """Obtiene todas las líneas disponibles"""
        cache_key = "template_lineas"
        result = cache.get(cache_key)
        
        if result is None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT 
                        CASE 
                            WHEN p.`descripción` LIKE '%A30%' THEN 'A30'
                            WHEN p.`descripción` LIKE '%A40%' THEN 'A40'
                            WHEN p.`descripción` LIKE '%Modena%' THEN 'Modena'
                            WHEN p.`descripción` LIKE '%Rotonda 640%' THEN 'Rotonda 640'
                            WHEN p.`descripción` LIKE '%Herrero%' THEN 'Herrero'
                            WHEN p.`descripción` LIKE '%Hydro%' THEN 'Hydro'
                            ELSE 'Estándar'
                        END as linea
                    FROM productos p
                    WHERE p.`descripción` NOT LIKE '*TRIAL%'
                    AND p.`descripción` IS NOT NULL
                    ORDER BY linea
                """)
                
                result = [{'code': row[0], 'label': row[0]} for row in cursor.fetchall() if row[0]]
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def get_marcos(cls, linea: str) -> List[Dict]:
        """Obtiene marcos disponibles por línea"""
        cache_key = f"marcos_{linea}"
        result = cache.get(cache_key)
        
        if result is None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT m.trial_id_1, m.`descripción`
                    FROM productos p
                    JOIN marco m ON p.id = m.`id producto`
                    WHERE p.`descripción` LIKE %s
                    AND p.`descripción` NOT LIKE '*TRIAL%'
                    AND m.`descripción` NOT LIKE '*TRIAL%'
                    ORDER BY m.`descripción`
                """, [f'%{linea}%'])
                
                result = [{'code': str(row[0]), 'label': row[1]} for row in cursor.fetchall()]
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def get_hojas(cls, marco_id: str) -> List[Dict]:
        """Obtiene hojas disponibles para un marco específico"""
        cache_key = f"hojas_{marco_id}"
        result = cache.get(cache_key)
        
        if result is None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT h.id, h.`descripción`
                    FROM hoja h
                    WHERE h.`id marco` = %s
                    AND h.`descripción` NOT LIKE '*TRIAL%'
                    ORDER BY h.`descripción`
                """, [marco_id])
                
                result = [{'code': str(row[0]), 'label': row[1]} for row in cursor.fetchall()]
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def get_interiores(cls, hoja_id: str) -> List[Dict]:
        """Obtiene interiores disponibles para una hoja específica"""
        cache_key = f"interiores_{hoja_id}"
        result = cache.get(cache_key)
        
        if result is None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT i.id, i.`descripción`
                    FROM interior i
                    WHERE i.`id hoja` = %s
                    AND i.`descripción` NOT LIKE '*TRIAL%'
                    ORDER BY i.`descripción`
                """, [hoja_id])
                
                result = [{'code': str(row[0]), 'label': row[1]} for row in cursor.fetchall()]
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def has_contravidrios(cls, interior_id: str) -> bool:
        """Verifica si un interior tiene contravidrios disponibles"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) > 0
                FROM contravidrio c
                WHERE c.`trial_id interior_2` = %s
            """, [interior_id])
            
            return cursor.fetchone()[0]
    
    @classmethod
    def has_mosquiteros(cls, hoja_id: str) -> bool:
        """Verifica si una hoja tiene mosquiteros disponibles"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) > 0
                FROM mosquitero m
                WHERE m.`id hoja` = %s
            """, [hoja_id])
            
            return cursor.fetchone()[0]
    
    @classmethod
    def has_vidrios_repartidos(cls, interior_id: str) -> bool:
        """Verifica si un interior tiene vidrios repartidos disponibles"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) > 0
                FROM vidrio_repartido vr
                WHERE vr.`id interior` = %s
            """, [interior_id])
            
            return cursor.fetchone()[0]