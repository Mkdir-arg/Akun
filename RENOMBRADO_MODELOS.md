# Renombrado de Modelos a Español - Resumen Completo

## Modelos Renombrados

### Core
- `Currency` → `Moneda`

### Catalog
- `UoM` → `UnidadMedida`
- `ProductCategory` → `CategoriaProducto`
- `TaxRate` → `TasaImpuesto`
- `Product` → `Producto`
- `PriceList` → `ListaPrecios`
- `PriceListRule` → `ReglaListaPrecios`

### CRM
- `Customer` → `Cliente`
- `Address` → `Direccion`
- `Contact` → `Contacto`
- `PaymentTerm` → `TerminoPago`
- `CustomerTag` → `EtiquetaCliente`
- `CustomerNote` → `NotaCliente`
- `CustomerFile` → `ArchivoCliente`

### Sales
- `Quote` → `Presupuesto`
- `QuoteItem` → `LineaPresupuesto`
- `Order` → `Pedido`
- `OrderItem` → `LineaPedido`

## Archivos Actualizados

### Modelos
- ✅ `apps/core/models.py`
- ✅ `apps/catalog/models.py`
- ✅ `apps/crm/models.py`
- ✅ `apps/sales/models.py`

### Admin
- ✅ `apps/catalog/admin.py`
- ✅ `apps/crm/admin.py`

### Serializers
- ✅ `apps/core/serializers.py`
- ✅ `apps/catalog/serializers.py`
- ✅ `apps/crm/serializers.py`
- ✅ `apps/sales/serializers.py`

### Views
- ✅ `apps/core/views.py`
- ✅ `apps/catalog/views.py`
- ✅ `apps/crm/views.py`
- ✅ `apps/sales/views.py`

### URLs
- ✅ `apps/core/urls.py`
- ✅ `apps/catalog/urls.py`
- ✅ `apps/crm/urls.py`
- ✅ `apps/sales/urls.py`

### Forms
- ✅ `apps/catalog/forms.py`
- ✅ `apps/crm/forms.py`

### Filters
- ✅ `apps/crm/filters.py`

### Management Commands
- ✅ `apps/core/management/commands/seed_currencies.py`
- ✅ `apps/catalog/management/commands/seed_catalog.py`
- ✅ `apps/crm/management/commands/seed_crm.py`

### Migraciones
- ✅ Eliminadas todas las migraciones existentes
- ✅ Recreados archivos `__init__.py` en carpetas de migraciones

## Próximos Pasos

1. **Crear nuevas migraciones:**
   ```bash
   python manage.py makemigrations
   ```

2. **Aplicar migraciones:**
   ```bash
   python manage.py migrate
   ```

3. **Crear datos iniciales:**
   ```bash
   python manage.py seed_currencies
   python manage.py seed_catalog
   python manage.py seed_crm
   ```

4. **Verificar funcionamiento:**
   - Probar API endpoints
   - Verificar admin de Django
   - Comprobar frontend React

## Notas Importantes

- Todos los nombres de modelos están ahora en español
- Se mantuvieron los nombres de tablas originales usando `db_table` en Meta
- Todas las referencias en código fueron actualizadas
- Los nombres de campos permanecen en inglés para mantener compatibilidad con APIs
- Las migraciones se recrearán desde cero con los nuevos nombres

## Tablas de Base de Datos

Las tablas mantendrán sus nombres originales en inglés para evitar problemas de compatibilidad:
- `core_currency` → Modelo `Moneda`
- `catalog_uom` → Modelo `UnidadMedida`
- `catalog_productcategory` → Modelo `CategoriaProducto`
- `catalog_taxrate` → Modelo `TasaImpuesto`
- `catalog_product` → Modelo `Producto`
- `catalog_pricelist` → Modelo `ListaPrecios`
- `catalog_pricelistrule` → Modelo `ReglaListaPrecios`
- `crm_customer` → Modelo `Cliente`
- `crm_address` → Modelo `Direccion`
- `crm_contact` → Modelo `Contacto`
- `crm_paymentterm` → Modelo `TerminoPago`
- `crm_customertag` → Modelo `EtiquetaCliente`
- `crm_customernote` → Modelo `NotaCliente`
- `crm_customerfile` → Modelo `ArchivoCliente`
- `sales_quote` → Modelo `Presupuesto`
- `sales_quoteitem` → Modelo `LineaPresupuesto`
- `sales_order` → Modelo `Pedido`
- `sales_orderitem` → Modelo `LineaPedido`