# ANÁLISIS DE FOREIGN KEYS - BASE DE DATOS AKUN

## RESUMEN EJECUTIVO

**Total de tablas:** 71  
**Total de foreign keys:** 58  
**Foreign keys problemáticas:** 0 (técnicamente funcionales)  
**Problemas de diseño identificados:** MÚLTIPLES

---

## PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **NOMBRES DE TABLAS CON ESPACIOS**
❌ **PROBLEMA GRAVE:** Muchas tablas tienen nombres con espacios, lo cual es una mala práctica:

- `tipo de accesorios`
- `contravidrio exterior`  
- `despiece accesorios contravidrio`
- `gest_cuentas clientes`
- `gest_pedido de accesorios`
- `vidrio repartido`
- Y muchas más...

**IMPACTO:** Requiere usar backticks (`) en todas las consultas SQL, genera errores de sintaxis, dificulta el mantenimiento.

**RECOMENDACIÓN:** Renombrar todas las tablas usando snake_case:
- `tipo de accesorios` → `tipo_accesorios`
- `contravidrio exterior` → `contravidrio_exterior`
- `gest_pedido de accesorios` → `gest_pedido_accesorios`

### 2. **INCONSISTENCIA EN CONVENCIONES DE NOMBRES**
❌ **PROBLEMA:** Mezcla de convenciones:
- Tablas Django: `accounts_user`, `catalog_producttemplate` (snake_case)
- Tablas importadas: `gest_clientes`, `tipo de accesorios` (espacios y guiones bajos mezclados)

### 3. **FOREIGN KEYS BIEN CONFIGURADAS TÉCNICAMENTE**
✅ **POSITIVO:** Las foreign keys existentes están correctamente configuradas:
- Todas las referencias apuntan a tablas y columnas existentes
- Reglas de CASCADE y NO ACTION apropiadas
- Constraints con nombres descriptivos

---

## ANÁLISIS DETALLADO DE FOREIGN KEYS

### TABLAS DE DJANGO (Bien estructuradas)

#### `accounts_user`
- ✅ `role_id` → `accounts_role.id` (SET NULL apropiado)

#### `catalog_templateattribute` 
- ✅ `template_id` → `catalog_producttemplate.id` (CASCADE apropiado)

#### `catalog_attributeoption`
- ✅ `attribute_id` → `catalog_templateattribute.id` (CASCADE apropiado)

### TABLAS DEL SISTEMA IMPORTADO (Problemas de nomenclatura)

#### Gestión de Clientes
- ✅ `gest_obras.id_cliente` → `gest_clientes.id`
- ✅ `gest_cuentas_clientes.trial_id_cliente_2` → `gest_clientes.id`

#### Gestión de Pedidos
- ✅ `gest_pedidos.trial_id_proveedor_2` → `gest_proveedores.trial_id_1`
- ✅ `gest_pedido_de_accesorios.id_pedido` → `gest_pedidos.id`
- ✅ `gest_pedido_de_perfiles.id_pedido` → `gest_pedidos.id`
- ✅ `gest_pedido_de_vidrios.id_pedido` → `gest_pedidos.id`

#### Estructura de Productos
- ✅ `marco.id_producto` → `productos.id`
- ✅ `hoja.id_marco` → `marco.trial_id_1`
- ✅ `interior.id_hoja` → `hoja.id`
- ✅ `contravidrio.trial_id_interior_2` → `interior.id`
- ✅ `cruces.trial_id_interior_2` → `interior.id`
- ✅ `mosquitero.id_hoja` → `hoja.id`
- ✅ `vidrio_repartido.id_interior` → `interior.id`

---

## RELACIONES FALTANTES POTENCIALES

### Tablas sin Foreign Keys que podrían necesitarlas:

1. **`gest_clientes`** - Sin relaciones geográficas
   - Podría relacionarse con tablas de provincia/municipio/localidad

2. **`productos`** - Sin categorización
   - Podría relacionarse con categorías o tipos de producto

3. **`moneda`** vs **`core_moneda`**
   - Duplicación de funcionalidad, una debería referenciar a la otra

4. **`modelos`** y **`modelos_productos`**
   - Relación unclear entre estas tablas

---

## RECOMENDACIONES PRIORITARIAS

### 1. **INMEDIATO - Renombrar Tablas**
```sql
-- Ejemplos de renombrado necesario
ALTER TABLE `tipo de accesorios` RENAME TO `tipo_accesorios`;
ALTER TABLE `contravidrio exterior` RENAME TO `contravidrio_exterior`;
ALTER TABLE `gest_pedido de accesorios` RENAME TO `gest_pedido_accesorios`;
-- ... continuar con todas las tablas con espacios
```

### 2. **CORTO PLAZO - Consolidar Duplicados**
- Evaluar `moneda` vs `core_moneda`
- Revisar `modelos` vs `modelos_productos`
- Unificar convenciones de nomenclatura

### 3. **MEDIANO PLAZO - Mejorar Relaciones**
- Agregar relaciones geográficas a `gest_clientes`
- Implementar categorización de productos
- Revisar estructura de despiece (muchas tablas similares)

### 4. **LARGO PLAZO - Refactoring**
- Considerar migrar tablas del sistema antiguo a estructura Django
- Implementar soft deletes donde sea apropiado
- Agregar índices para mejorar performance

---

## CONCLUSIÓN

**Estado actual:** Las foreign keys están técnicamente bien implementadas y funcionan correctamente.

**Problema principal:** La nomenclatura inconsistente y el uso de espacios en nombres de tablas genera problemas de mantenimiento y legibilidad.

**Prioridad:** ALTA - Renombrar tablas con espacios antes de continuar desarrollo.

**Riesgo:** MEDIO - El sistema funciona pero es difícil de mantener y propenso a errores de sintaxis SQL.