# API de Plantillas de Productos

## Endpoints Disponibles

### Plantillas

#### Listar plantillas
```
GET /api/templates/
```

Parámetros de consulta:
- `class`: Filtrar por clase (VENTANA, PUERTA, ACCESORIO)
- `line_name`: Filtrar por nombre de línea
- `active`: Filtrar por estado (true/false)

#### Crear plantilla
```
POST /api/templates/
```

Payload:
```json
{
  "product_class": "VENTANA",
  "line_name": "Módena",
  "code": "ventana-modena",
  "base_price_net": "50000.00",
  "currency": "ARS",
  "requires_dimensions": true,
  "is_active": true
}
```

#### Obtener plantilla
```
GET /api/templates/{id}/
```

#### Actualizar plantilla
```
PATCH /api/templates/{id}/
```

#### Clonar plantilla
```
POST /api/templates/{id}/clone/
```

#### Preview de precio
```
POST /api/templates/{id}/preview_pricing/
```

Payload:
```json
{
  "selections": {
    "color": "negro-mate",
    "hojas": "2h",
    "contramarco": true,
    "vidrio": "float-4mm"
  },
  "width_mm": 1300,
  "height_mm": 1200,
  "currency": "ARS",
  "iva_pct": 21.0
}
```

Respuesta:
```json
{
  "calc": {
    "area_m2": 1.56,
    "perimeter_m": 5.0
  },
  "price": {
    "net": 152345.50,
    "tax": 31992.56,
    "gross": 184338.06
  },
  "breakdown": [
    {"source":"template_base", "mode":"ABS", "value": 50000.00},
    {"source":"color/negro-mate", "mode":"FACTOR", "factor": 1.08, "applied_on": 50000.00, "delta": 4000.00},
    {"source":"hojas/2h", "mode":"ABS", "value": 12000.00},
    {"source":"contramarco/true", "mode":"PERIMETER", "perimeter_m": 5.0, "unit": 1500.00, "value": 7500.00},
    {"source":"vidrio/float-4mm", "mode":"PER_M2", "m2": 1.56, "unit": 8900.00, "value": 13884.00}
  ],
  "currency": "ARS"
}
```

### Atributos

#### Listar atributos
```
GET /api/attributes/?template_id={template_id}
```

#### Crear atributo
```
POST /api/attributes/
```

Payload:
```json
{
  "template_id": 1,
  "name": "Color",
  "code": "color",
  "type": "SELECT",
  "is_required": true,
  "order": 1,
  "rules_json": {}
}
```

#### Actualizar atributo
```
PATCH /api/attributes/{id}/
```

#### Eliminar atributo
```
DELETE /api/attributes/{id}/
```

#### Reordenar atributo
```
POST /api/attributes/{id}/reorder/
```

Payload:
```json
{
  "new_order": 3
}
```

### Opciones

#### Listar opciones
```
GET /api/options/?attribute_id={attribute_id}
```

#### Crear opción
```
POST /api/options/
```

Payload:
```json
{
  "attribute_id": 1,
  "label": "Negro Mate",
  "code": "negro-mate",
  "pricing_mode": "FACTOR",
  "price_value": "1.0800",
  "currency": "ARS",
  "order": 1,
  "is_default": false
}
```

#### Actualizar opción
```
PATCH /api/options/{id}/
```

#### Eliminar opción
```
DELETE /api/options/{id}/
```

#### Reordenar opción
```
POST /api/options/{id}/reorder/
```

## Tipos de Atributos

- `SELECT`: Lista desplegable
- `BOOLEAN`: Verdadero/Falso
- `NUMBER`: Número
- `COLOR`: Color
- `MEASURE_MM`: Medida en milímetros

## Modos de Precio

- `ABS`: Suma absoluta por ítem
- `PER_M2`: Precio por m²
- `PERIMETER`: Precio por perímetro (m)
- `FACTOR`: Factor multiplicativo (x)

## Cargar Datos de Ejemplo

Para cargar la plantilla Módena de ejemplo:

```bash
python manage.py loaddata plantilla_modena.json
```

## Ejecutar Tests

```bash
python manage.py test apps.catalog.tests
```

## Componentes React

Los componentes están en `src/components/templates/`:

- `TemplateList.tsx`: Lista de plantillas
- `TemplateEditor.tsx`: Editor principal
- `AttributeTable.tsx`: Tabla de atributos
- `OptionTable.tsx`: Tabla de opciones
- `PreviewPanel.tsx`: Panel de preview de precios

## Uso de los Componentes

```tsx
import TemplateList from './components/templates/TemplateList';
import TemplateEditor from './components/templates/TemplateEditor';

// Lista de plantillas
<TemplateList />

// Editor de plantilla
<TemplateEditor templateId="1" />
```