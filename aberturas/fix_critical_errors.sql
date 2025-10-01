-- SCRIPT PARA CORREGIR ERRORES CRÍTICOS EN BASE DE DATOS AKUN
-- EJECUTAR EN ORDEN SECUENCIAL

-- =====================================================
-- 1. RENOMBRAR TABLAS CON ESPACIOS A SNAKE_CASE
-- =====================================================

-- Tablas de tipos y accesorios
ALTER TABLE `tipo de accesorios` RENAME TO `tipo_accesorios`;
ALTER TABLE `tipo de interiores` RENAME TO `tipo_interiores`;
ALTER TABLE `tipos colocación` RENAME TO `tipos_colocacion`;

-- Tablas de contravidrios
ALTER TABLE `contravidrio exterior` RENAME TO `contravidrio_exterior`;

-- Tablas de vidrios
ALTER TABLE `vidrio repartido` RENAME TO `vidrio_repartido`;

-- Tablas de gestión con espacios
ALTER TABLE `gest_cuentas clientes` RENAME TO `gest_cuentas_clientes`;
ALTER TABLE `gest_cuentas proveedores` RENAME TO `gest_cuentas_proveedores`;
ALTER TABLE `gest_historial de obra` RENAME TO `gest_historial_obra`;
ALTER TABLE `gest_ingreso de accesorios` RENAME TO `gest_ingreso_accesorios`;
ALTER TABLE `gest_ingreso de perfiles` RENAME TO `gest_ingreso_perfiles`;
ALTER TABLE `gest_ingreso de vidrios` RENAME TO `gest_ingreso_vidrios`;
ALTER TABLE `gest_pedido de accesorios` RENAME TO `gest_pedido_accesorios`;
ALTER TABLE `gest_pedido de perfiles` RENAME TO `gest_pedido_perfiles`;
ALTER TABLE `gest_pedido de vidrios` RENAME TO `gest_pedido_vidrios`;

-- Tablas de despiece con espacios
ALTER TABLE `despiece accesorios contravidrio` RENAME TO `despiece_accesorios_contravidrio`;
ALTER TABLE `despiece accesorios contravidrio exterior` RENAME TO `despiece_accesorios_contravidrio_exterior`;
ALTER TABLE `despiece accesorios cruces` RENAME TO `despiece_accesorios_cruces`;
ALTER TABLE `despiece accesorios hoja` RENAME TO `despiece_accesorios_hoja`;
ALTER TABLE `despiece accesorios interior` RENAME TO `despiece_accesorios_interior`;
ALTER TABLE `despiece accesorios marco` RENAME TO `despiece_accesorios_marco`;
ALTER TABLE `despiece accesorios mosquitero` RENAME TO `despiece_accesorios_mosquitero`;
ALTER TABLE `despiece accesorios vidrio repartido` RENAME TO `despiece_accesorios_vidrio_repartido`;
ALTER TABLE `despiece cruces` RENAME TO `despiece_cruces`;
ALTER TABLE `despiece interior` RENAME TO `despiece_interior`;
ALTER TABLE `despiece interior mosquitero` RENAME TO `despiece_interior_mosquitero`;
ALTER TABLE `despiece perfiles contravidrios` RENAME TO `despiece_perfiles_contravidrios`;
ALTER TABLE `despiece perfiles contravidrios exterior` RENAME TO `despiece_perfiles_contravidrios_exterior`;
ALTER TABLE `despiece perfiles hojas` RENAME TO `despiece_perfiles_hojas`;
ALTER TABLE `despiece perfiles marcos` RENAME TO `despiece_perfiles_marcos`;
ALTER TABLE `despiece perfiles mosquitero` RENAME TO `despiece_perfiles_mosquitero`;
ALTER TABLE `despiece perfiles vidrio repartido` RENAME TO `despiece_perfiles_vidrio_repartido`;

-- Otras tablas con espacios
ALTER TABLE `encabezados y pies` RENAME TO `encabezados_pies`;
ALTER TABLE `recortes de perfiles` RENAME TO `recortes_perfiles`;

-- =====================================================
-- 2. ACTUALIZAR FOREIGN KEYS DESPUÉS DEL RENOMBRADO
-- =====================================================

-- Las foreign keys se actualizan automáticamente con el renombrado de tablas
-- Pero verificamos que las referencias sigan siendo correctas

-- =====================================================
-- 3. CREAR ÍNDICES FALTANTES PARA MEJORAR PERFORMANCE
-- =====================================================

-- Índices para tablas de gestión
CREATE INDEX idx_gest_clientes_nombre ON gest_clientes(nombre);
CREATE INDEX idx_gest_obras_cliente ON gest_obras(id_cliente);
CREATE INDEX idx_gest_pedidos_proveedor ON gest_pedidos(trial_id_proveedor_2);

-- Índices para estructura de productos
CREATE INDEX idx_marco_producto ON marco(id_producto);
CREATE INDEX idx_hoja_marco ON hoja(id_marco);
CREATE INDEX idx_interior_hoja ON interior(id_hoja);

-- =====================================================
-- 4. VERIFICACIÓN POST-RENOMBRADO
-- =====================================================

-- Verificar que todas las tablas fueron renombradas correctamente
SELECT 
    TABLE_NAME,
    CASE 
        WHEN TABLE_NAME LIKE '% %' THEN 'PENDIENTE'
        ELSE 'OK'
    END as STATUS
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'akun' 
AND TABLE_NAME LIKE '% %';

-- Verificar foreign keys después del renombrado
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'akun' 
AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;