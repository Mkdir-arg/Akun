from collections import defaultdict
from decimal import Decimal
import unicodedata

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import (
    AttributeOption,
    AttributeType,
    PricingMode,
    ProductClass,
    ProductTemplate,
    RenderVariant,
    TemplateAttribute,
    TemplateCategory,
)
from apps.legacy.models import (
    LegacyContravidrio,
    LegacyFrame,
    LegacyInterior,
    LegacyLeaf,
    LegacyMosquitero,
    LegacyProduct,
    LegacyVidrioRepartido,
)


LINE_KEYWORDS = [
    ("A30", "A30"),
    ("A40", "A40"),
    ("MODENA", "Modena"),
    ("ROTONDA 640", "Rotonda 640"),
    ("HERRERO", "Herrero"),
    ("HYDRO", "Hydro"),
]


class Command(BaseCommand):
    help = "Sincroniza plantillas con datos legacy agrupadas por extrusora"

    def handle(self, *args, **options):
        products = LegacyProduct.objects.usable().select_related("extrusora").order_by("descripcion")
        if not products.exists():
            self.stdout.write(self.style.WARNING("No se encontraron productos legacy para sincronizar."))
            return
        cache.clear()

        created = 0
        updated = 0
        skipped = 0

        for product in products:
            frames = self._collect_frames(product)
            if not frames:
                skipped += 1
                continue

            with transaction.atomic():
                category = self._ensure_category(product)
                template, was_created = self._ensure_template(product, category)
                self._sync_attributes(template, product, frames)

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write("=== SINCRONIZACION DE PLANTILLAS LEGACY ===")
        self.stdout.write(f"  Plantillas nuevas: {created}")
        self.stdout.write(f"  Plantillas actualizadas: {updated}")
        self.stdout.write(f"  Productos sin marcos asociados (omitidos): {skipped}")
        self.stdout.write(self.style.SUCCESS("Sincronizacion completada."))

    # ------------------------------------------------------------------
    def _ensure_category(self, product):
        extrusora = product.extrusora
        legacy_id = extrusora.id if extrusora else 0
        name = (extrusora.nombre or "Extrusora sin nombre") if extrusora else "Sin extrusora"
        slug = slugify(name) or f"extrusora-{legacy_id or 'na'}"

        category, _ = TemplateCategory.objects.get_or_create(
            legacy_extrusora_id=legacy_id,
            defaults={
                "legacy_extrusora_name": extrusora.nombre if extrusora else "",
                "name": name,
                "slug": slug,
                "description": extrusora.nombre or "",
            },
        )

        category.legacy_extrusora_name = extrusora.nombre if extrusora else ""
        category.name = name
        category.description = extrusora.nombre or ""
        category.save(update_fields=["legacy_extrusora_name", "name", "description", "updated_at"])
        return category

    def _ensure_template(self, product, category):
        code = f"legacy-{product.id}"
        line_name = self._infer_line_name(product.descripcion)
        product_class = self._infer_product_class(product.descripcion)

        defaults = {
            "product_class": product_class,
            "line_name": line_name,
            "base_price_net": Decimal("0"),
            "currency": "ARS",
            "requires_dimensions": True,
            "is_active": True,
            "version": 1,
        }

        template, created = ProductTemplate.objects.get_or_create(code=code, defaults=defaults)

        template.product_class = product_class
        template.line_name = line_name
        template.is_active = True
        template.category = category
        template.legacy_product_id = product.id
        template.legacy_extrusora_id = product.extrusora.id if product.extrusora else None
        template.legacy_extrusora_name = product.extrusora.nombre if product.extrusora else ""
        template.legacy_metadata = {
            "description": product.descripcion,
            "tipo_id": product.tipo_id,
            "linea_id": product.linea_id,
        }
        template.save(update_fields=[
            "product_class",
            "line_name",
            "is_active",
            "category",
            "legacy_product_id",
            "legacy_extrusora_id",
            "legacy_extrusora_name",
            "legacy_metadata",
            "modified_at",
        ])

        return template, created

    def _collect_frames(self, product):
        frames = LegacyFrame.objects.filter(product_id=product.id).order_by("descripcion")
        return [frame for frame in frames if not self._is_trial(frame.descripcion)]

    def _sync_attributes(self, template, product, frames):
        leaves_by_frame, interiors_by_leaf = self._collect_leaf_and_interior_data(frames)
        optional_data = self._collect_optional_components(interiors_by_leaf)

        expected_codes = []
        order_counter = 1

        linea_attr = self._ensure_attribute(
            template,
            code="linea",
            name="Linea",
            order=order_counter,
            attr_type=AttributeType.SELECT,
            render_variant=RenderVariant.SELECT,
            rules={"legacy_source": "legacy.product"},
            legacy_payload={"product_id": product.id},
        )
        expected_codes.append(linea_attr.code)
        self._sync_options(
            linea_attr,
            [
                {
                    "code": slugify(template.line_name) or f"linea-{product.id}",
                    "label": template.line_name,
                    "order": 1,
                    "legacy_payload": {"product_id": product.id},
                    "is_default": True,
                }
            ],
        )
        order_counter += 1

        marco_attr = self._ensure_attribute(
            template,
            code="marco",
            name="Marco",
            order=order_counter,
            attr_type=AttributeType.SELECT,
            render_variant=RenderVariant.SELECT,
            rules={
                "depends_on": ["linea"],
                "filters_next": ["hoja"],
                "legacy_source": "legacy.marco",
            },
            legacy_payload={"product_id": product.id},
        )
        expected_codes.append(marco_attr.code)
        marco_options = []
        for index, frame in enumerate(frames, start=1):
            marco_options.append(
                {
                    "code": str(frame.id),
                    "label": frame.descripcion or f"Marco {frame.id}",
                    "order": index,
                    "legacy_payload": {
                        "marco_id": frame.id,
                        "product_id": product.id,
                    },
                }
            )
        self._sync_options(marco_attr, marco_options)
        order_counter += 1

        hoja_attr = self._ensure_attribute(
            template,
            code="hoja",
            name="Hoja",
            order=order_counter,
            attr_type=AttributeType.SELECT,
            render_variant=RenderVariant.SELECT,
            rules={
                "depends_on": ["marco"],
                "filters_next": ["interior"],
                "legacy_source": "legacy.hoja",
            },
            legacy_payload={"product_id": product.id},
        )
        expected_codes.append(hoja_attr.code)
        hoja_options = []
        for frame in frames:
            leaves = leaves_by_frame.get(frame.id, [])
            for idx, leaf in enumerate(leaves, start=1):
                hoja_options.append(
                    {
                        "code": str(leaf.id),
                        "label": leaf.descripcion or f"Hoja {leaf.id}",
                        "order": idx,
                        "legacy_payload": {
                            "hoja_id": leaf.id,
                            "marco_id": frame.id,
                            "product_id": product.id,
                        },
                    }
                )
        self._sync_options(hoja_attr, hoja_options)
        order_counter += 1

        interior_attr = self._ensure_attribute(
            template,
            code="interior",
            name="Interior",
            order=order_counter,
            attr_type=AttributeType.SELECT,
            render_variant=RenderVariant.SELECT,
            rules={
                "depends_on": ["hoja"],
                "legacy_source": "legacy.interior",
            },
            legacy_payload={"product_id": product.id},
        )
        expected_codes.append(interior_attr.code)
        interior_options = []
        for leaf_id, interiors in interiors_by_leaf.items():
            for idx, interior in enumerate(interiors, start=1):
                interior_options.append(
                    {
                        "code": str(interior.id),
                        "label": interior.descripcion or f"Interior {interior.id}",
                        "order": idx,
                        "legacy_payload": {
                            "interior_id": interior.id,
                            "hoja_id": leaf_id,
                            "product_id": product.id,
                        },
                    }
                )
        self._sync_options(interior_attr, interior_options)
        order_counter += 1

        dimensiones_attr = self._ensure_attribute(
            template,
            code="dimensiones",
            name="Dimensiones",
            order=order_counter,
            attr_type=AttributeType.DIMENSIONS_MM,
            render_variant=RenderVariant.SELECT,
            rules={"legacy_source": "legacy.dimensiones"},
            legacy_payload={"product_id": product.id},
            extra_kwargs={
                "min_width": 300,
                "max_width": 3000,
                "min_height": 400,
                "max_height": 2500,
                "step_mm": 10,
            },
        )
        expected_codes.append(dimensiones_attr.code)
        order_counter += 1

        cantidad_attr = self._ensure_attribute(
            template,
            code="cantidad",
            name="Cantidad",
            order=order_counter,
            attr_type=AttributeType.QUANTITY,
            render_variant=RenderVariant.SELECT,
            rules={"legacy_source": "legacy.cantidad"},
            legacy_payload={"product_id": product.id},
            extra_kwargs={
                "min_value": Decimal("1"),
                "max_value": Decimal("100"),
                "step_value": Decimal("1"),
                "unit_label": "unidades",
            },
        )
        expected_codes.append(cantidad_attr.code)
        order_counter += 1

        if optional_data["contravidrio"]:
            contravidrio_attr = self._ensure_attribute(
                template,
                code="contravidrio",
                name="Contravidrio",
                order=order_counter,
                attr_type=AttributeType.BOOLEAN,
                render_variant=RenderVariant.SELECT,
                rules={
                    "conditional": True,
                    "depends_on": ["interior"],
                    "legacy_source": "legacy.contravidrio",
                },
                legacy_payload={"interior_ids": optional_data["contravidrio"]},
                required=False,
            )
            expected_codes.append(contravidrio_attr.code)
            order_counter += 1

        if optional_data["mosquitero"]:
            mosquitero_attr = self._ensure_attribute(
                template,
                code="mosquitero",
                name="Mosquitero",
                order=order_counter,
                attr_type=AttributeType.BOOLEAN,
                render_variant=RenderVariant.SELECT,
                rules={
                    "conditional": True,
                    "depends_on": ["hoja"],
                    "legacy_source": "legacy.mosquitero",
                },
                legacy_payload={"hoja_ids": optional_data["mosquitero"]},
                required=False,
            )
            expected_codes.append(mosquitero_attr.code)
            order_counter += 1

        if optional_data["vidrio_repartido"]:
            vidrio_attr = self._ensure_attribute(
                template,
                code="vidrio_repartido",
                name="Vidrio Repartido",
                order=order_counter,
                attr_type=AttributeType.BOOLEAN,
                render_variant=RenderVariant.SELECT,
                rules={
                    "conditional": True,
                    "depends_on": ["interior"],
                    "legacy_source": "legacy.vidrio_repartido",
                },
                legacy_payload={"interior_ids": optional_data["vidrio_repartido"]},
                required=False,
            )
            expected_codes.append(vidrio_attr.code)
            order_counter += 1

        template.attributes.exclude(code__in=expected_codes).delete()

    def _collect_leaf_and_interior_data(self, frames):
        leaves_by_frame = defaultdict(list)
        interiors_by_leaf = defaultdict(list)

        frame_ids = [frame.id for frame in frames]
        if not frame_ids:
            return leaves_by_frame, interiors_by_leaf

        leaves = LegacyLeaf.objects.filter(marco_id__in=frame_ids).order_by("descripcion")
        leaves = [leaf for leaf in leaves if not self._is_trial(leaf.descripcion)]
        for leaf in leaves:
            leaves_by_frame[leaf.marco_id].append(leaf)

        hoja_ids = [leaf.id for leaf in leaves]
        if hoja_ids:
            interiors = LegacyInterior.objects.filter(hoja_id__in=hoja_ids).order_by("descripcion")
            interiors = [item for item in interiors if not self._is_trial(item.descripcion)]
            for interior in interiors:
                interiors_by_leaf[interior.hoja_id].append(interior)

        return leaves_by_frame, interiors_by_leaf

    def _collect_optional_components(self, interiors_by_leaf):
        interior_ids = [interior.id for interiors in interiors_by_leaf.values() for interior in interiors]
        hoja_ids = list(interiors_by_leaf.keys())

        contravidrio_codes = set()
        mosquitero_codes = set()
        vidrio_codes = set()

        if interior_ids:
            contravidrio_codes = {
                str(code)
                for code in LegacyContravidrio.objects.filter(interior_id__in=interior_ids).values_list("interior_id", flat=True)
            }
            vidrio_codes = {
                str(code)
                for code in LegacyVidrioRepartido.objects.filter(interior_id__in=interior_ids).values_list("interior_id", flat=True)
            }

        if hoja_ids:
            mosquitero_codes = {
                str(code)
                for code in LegacyMosquitero.objects.filter(hoja_id__in=hoja_ids).values_list("hoja_id", flat=True)
            }

        return {
            "contravidrio": sorted(contravidrio_codes),
            "mosquitero": sorted(mosquitero_codes),
            "vidrio_repartido": sorted(vidrio_codes),
        }

    def _ensure_attribute(
        self,
        template,
        *,
        code,
        name,
        order,
        attr_type,
        render_variant,
        rules,
        legacy_payload,
        extra_kwargs=None,
        required=True,
    ):
        defaults = {
            "name": name,
            "type": attr_type,
            "order": order,
            "render_variant": render_variant,
            "rules_json": rules,
            "legacy_payload": legacy_payload,
            "is_required": required,
        }
        if extra_kwargs:
            defaults.update(extra_kwargs)

        attribute, _ = TemplateAttribute.objects.get_or_create(
            template=template,
            code=code,
            defaults=defaults,
        )

        attribute.name = name
        attribute.type = attr_type
        attribute.order = order
        attribute.render_variant = render_variant
        attribute.rules_json = rules
        attribute.legacy_payload = legacy_payload
        attribute.is_required = required

        if extra_kwargs:
            for key, value in extra_kwargs.items():
                setattr(attribute, key, value)

        attribute.save()
        return attribute

    def _sync_options(self, attribute, option_payloads):
        existing_codes = set()
        for payload in option_payloads:
            code = payload["code"]
            option, _ = AttributeOption.objects.get_or_create(
                attribute=attribute,
                code=code,
                defaults={
                    "label": payload["label"],
                    "order": payload.get("order", 1),
                    "pricing_mode": PricingMode.ABS,
                    "price_value": Decimal("0"),
                    "currency": attribute.template.currency,
                },
            )
            option.label = payload["label"]
            option.order = payload.get("order", option.order)
            option.pricing_mode = PricingMode.ABS
            option.price_value = Decimal("0")
            option.currency = attribute.template.currency
            option.is_default = payload.get("is_default", False)
            option.legacy_payload = payload.get("legacy_payload", {})
            option.save()
            existing_codes.add(code)

        attribute.options.exclude(code__in=list(existing_codes)).delete()

    # ------------------------------------------------------------------
    def _infer_product_class(self, description):
        normalized = self._normalize(description)
        if "VENTANA" in normalized or "PANO FIJO" in normalized:
            return ProductClass.VENTANA
        if "PUERTA" in normalized:
            return ProductClass.PUERTA
        return ProductClass.ACCESORIO

    def _infer_line_name(self, description):
        normalized = self._normalize(description)
        for needle, label in LINE_KEYWORDS:
            if needle in normalized:
                return label
        return "Estandar"

    def _normalize(self, value):
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
        return ascii_only.upper()

    def _is_trial(self, value):
        if not value:
            return False
        return value.strip().upper().startswith("*TRIAL")
