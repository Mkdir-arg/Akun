from typing import Dict, List, Optional

from django.core.cache import cache
from django.db import connection
from django.db.models import Q

from apps.catalog.models import (
    AttributeOption,
    ProductTemplate,
    TemplateAttribute,
    TemplateCategory,
)


class TemplateFilterService:
    """Servicio para filtrado dinamico de opciones de plantillas"""

    CACHE_TIMEOUT = 3600  # 1 hora

    # ------------------------- Categorias -------------------------
    @classmethod
    def get_categories(cls) -> List[Dict]:
        cache_key = "template_categories"
        result = cache.get(cache_key)
        if result is not None:
            return result

        categories = (
            TemplateCategory.objects.prefetch_related("templates")
            .order_by("order", "name")
        )

        payload = []
        for category in categories:
            templates_qs = category.templates.all()
            if not templates_qs.exists():
                continue

            total_templates = templates_qs.count()
            active_templates = templates_qs.filter(is_active=True).count()
            class_counter: Dict[str, int] = {}
            lines: Dict[str, int] = {}
            for template in templates_qs:
                class_counter[template.product_class] = class_counter.get(template.product_class, 0) + 1
                lines[template.line_name] = lines.get(template.line_name, 0) + 1

            payload.append(
                {
                    "id": category.id,
                    "legacy_extrusora_id": category.legacy_extrusora_id,
                    "legacy_extrusora_name": category.legacy_extrusora_name,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                    "templates": total_templates,
                    "active_templates": active_templates,
                    "product_classes": class_counter,
                    "lines": lines,
                }
            )

        cache.set(cache_key, payload, cls.CACHE_TIMEOUT)
        return payload

    # ------------------------- Flujo clasico -------------------------
    @classmethod
    def get_lineas(cls, category_id: Optional[int] = None, extrusora_id: Optional[int] = None) -> List[Dict]:
        cache_key = f'template_lineas_{category_id or "all"}_{extrusora_id or "all"}'
        result = cache.get(cache_key)
        if result is None:
            result = cls._lineas_from_templates(category_id=category_id, extrusora_id=extrusora_id)
            if not result and category_id is None and extrusora_id is None:
                result = cls._lineas_from_legacy()
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result

    @classmethod
    def get_marcos(cls, linea: str) -> List[Dict]:
        cache_key = f"marcos_{linea}"
        result = cache.get(cache_key)
        if result is None:
            result = cls._marcos_from_templates(linea)
            if not result:
                result = cls._marcos_from_legacy(linea)
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result

    @classmethod
    def get_hojas(cls, marco_id: str) -> List[Dict]:
        cache_key = f"hojas_{marco_id}"
        result = cache.get(cache_key)
        if result is None:
            result = cls._hojas_from_templates(marco_id)
            if not result:
                result = cls._hojas_from_legacy(marco_id)
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result

    @classmethod
    def get_interiores(cls, hoja_id: str) -> List[Dict]:
        cache_key = f"interiores_{hoja_id}"
        result = cache.get(cache_key)
        if result is None:
            result = cls._interiores_from_templates(hoja_id)
            if not result:
                result = cls._interiores_from_legacy(hoja_id)
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result

    @classmethod
    def has_contravidrios(cls, interior_id: str) -> bool:
        if cls._legacy_flag_exists("contravidrio", interior_id):
            return True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) > 0 FROM contravidrio WHERE idinterior = %s",
                [interior_id],
            )
            return cursor.fetchone()[0]

    @classmethod
    def has_mosquiteros(cls, hoja_id: str) -> bool:
        if cls._legacy_flag_exists("mosquitero", hoja_id):
            return True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) > 0 FROM mosquitero WHERE idhoja = %s",
                [hoja_id],
            )
            return cursor.fetchone()[0]

    @classmethod
    def has_vidrios_repartidos(cls, interior_id: str) -> bool:
        if cls._legacy_flag_exists("vidrio_repartido", interior_id):
            return True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) > 0 FROM vidrio_repartido WHERE idinterior = %s",
                [interior_id],
            )
            return cursor.fetchone()[0]

    # ------------------------------------------------------------------
    @classmethod
    def _lineas_from_templates(cls, category_id: Optional[int] = None, extrusora_id: Optional[int] = None) -> List[Dict]:
        templates = ProductTemplate.objects.filter(is_active=True)
        if category_id:
            templates = templates.filter(category_id=category_id)
        if extrusora_id is not None:
            templates = templates.filter(legacy_extrusora_id=extrusora_id)
        lineas_qs = (
            templates
            .exclude(line_name__isnull=True)
            .exclude(line_name__exact="")
            .values_list("line_name", flat=True)
            .distinct()
            .order_by("line_name")
        )
        return [{"code": linea, "label": linea} for linea in lineas_qs if linea]

    @classmethod
    def _lineas_from_legacy(cls) -> List[Dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT 
                    CASE 
                        WHEN p.Descripci_n LIKE '%A30%' THEN 'A30'
                        WHEN p.Descripci_n LIKE '%A40%' THEN 'A40'
                        WHEN p.Descripci_n LIKE '%Modena%' THEN 'Modena'
                        WHEN p.Descripci_n LIKE '%Rotonda 640%' THEN 'Rotonda 640'
                        WHEN p.Descripci_n LIKE '%Herrero%' THEN 'Herrero'
                        WHEN p.Descripci_n LIKE '%Hydro%' THEN 'Hydro'
                        ELSE 'Estandar'
                    END as linea
                FROM productos p
                WHERE p.Descripci_n NOT LIKE '*TRIAL%'
                AND p.Descripci_n IS NOT NULL
                ORDER BY linea
                """
            )
            return [{"code": row[0], "label": row[0]} for row in cursor.fetchall() if row[0]]

    @classmethod
    def _marcos_from_templates(cls, linea: str) -> List[Dict]:
        templates = ProductTemplate.objects.filter(is_active=True, line_name=linea)
        if not templates.exists():
            return []

        options = AttributeOption.objects.filter(
            attribute__template__in=templates,
            attribute__code="marco",
        ).order_by("label", "code")

        result = []
        seen = set()
        for option in options:
            code = option.code
            if not code or code in seen:
                continue
            result.append({"code": code, "label": option.label})
            seen.add(code)
        return result

    @classmethod
    def _marcos_from_legacy(cls, linea: str) -> List[Dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT m.Id, m.Descripci_n
                FROM productos p
                JOIN marco m ON p.Id = m.idproducto
                WHERE p.Descripci_n LIKE %s
                AND p.Descripci_n NOT LIKE '*TRIAL%'
                AND m.Descripci_n NOT LIKE '*TRIAL%'
                ORDER BY m.Descripci_n
                """,
                [f"%{linea}%"],
            )
            return [{"code": str(row[0]), "label": row[1]} for row in cursor.fetchall()]

    @classmethod
    def _hojas_from_templates(cls, marco_id: str) -> List[Dict]:
        options = AttributeOption.objects.filter(
            attribute__code="hoja",
            attribute__template__is_active=True,
        )

        target = str(marco_id)
        result = []
        seen = set()
        for option in options:
            payload = option.legacy_payload or {}
            if str(payload.get("marco_id")) != target:
                continue
            code = option.code
            if not code or code in seen:
                continue
            result.append({"code": code, "label": option.label})
            seen.add(code)
        return result

    @classmethod
    def _hojas_from_legacy(cls, marco_id: str) -> List[Dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT h.Id, h.Descripci_n
                FROM hoja h
                WHERE h.idmarco = %s
                AND h.Descripci_n NOT LIKE '*TRIAL%'
                ORDER BY h.Descripci_n
                """,
                [marco_id],
            )
            return [{"code": str(row[0]), "label": row[1]} for row in cursor.fetchall()]

    @classmethod
    def _interiores_from_templates(cls, hoja_id: str) -> List[Dict]:
        options = AttributeOption.objects.filter(
            attribute__code="interior",
            attribute__template__is_active=True,
        )

        target = str(hoja_id)
        result = []
        seen = set()
        for option in options:
            payload = option.legacy_payload or {}
            if str(payload.get("hoja_id")) != target:
                continue
            code = option.code
            if not code or code in seen:
                continue
            result.append({"code": code, "label": option.label})
            seen.add(code)
        return result

    @classmethod
    def _interiores_from_legacy(cls, hoja_id: str) -> List[Dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT i.Id, i.Descripci_n
                FROM interior i
                WHERE i.Idhoja = %s
                AND i.Descripci_n NOT LIKE '*TRIAL%'
                ORDER BY i.Descripci_n
                """,
                [hoja_id],
            )
            return [{"code": str(row[0]), "label": row[1]} for row in cursor.fetchall()]

    @classmethod
    def _legacy_flag_exists(cls, attribute_code: str, lookup_value: str) -> bool:
        target = str(lookup_value)

        if attribute_code == "mosquitero":
            payload_key = "hoja_ids"
        else:
            payload_key = "interior_ids"

        filters = Q(code=attribute_code, template__is_active=True)
        filters &= Q(legacy_payload__has_key=payload_key)
        filters &= Q(**{f"legacy_payload__{payload_key}__contains": [target]})

        return TemplateAttribute.objects.filter(filters).exists()

    @staticmethod
    def _safe_int(value: Optional[str]) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
