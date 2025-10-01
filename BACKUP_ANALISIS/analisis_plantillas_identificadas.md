# ANÁLISIS DE PLANTILLAS IDENTIFICADAS

## 📊 RESUMEN DE DATOS ENCONTRADOS

**Total de registros:**
- **111 productos** (base de plantillas)
- **229 marcos**
- **421 hojas**
- **480 interiores**
- **0 plantillas Django** (sistema nuevo)

---

## 🏗️ ESTRUCTURA JERÁRQUICA IDENTIFICADA

```
PRODUCTO (base)
    ↓
MARCO (configuración específica)
    ↓
HOJA (tipo de apertura)
    ↓
INTERIOR (tipo de vidrio/relleno)
    ↓
COMPONENTES OPCIONALES:
    - Contravidrio
    - Mosquitero
    - Vidrio repartido
    - Cruces
```

---

## 🚪 PLANTILLAS PRINCIPALES IDENTIFICADAS

### **VENTANAS:**
1. **Ventana de abrir A30** - 7 productos
2. **Ventana Oscilobatiente Rotonda 640** - 4 productos
3. **Ventana de abrir** - 3 productos
4. **Ventana Corrediza** - 2 productos
5. **Ventana Corrediza A30** - 2 productos
6. **Ventana de abrir Modena Doble Contacto** - 2 productos
7. **Ventana Banderola Modena** - 1 producto
8. **Ventana corrediza 90º Módena** - 1 producto
9. **Ventana Desplazable Módena** - 1 producto
10. **Ventana de abrir A40** - 1 producto
11. **Ventana Desplazable A40** - 1 producto
12. **Ventana Banderola A40** - 1 producto

### **PUERTAS:**
1. **Puerta** - 3 productos
2. **Puerta de abrir Modena** - 2 productos
3. **Puerta placa** - 1 producto
4. **Puerta de Abrir A30** - 1 producto
5. **Puerta de rebatir Rotonda 640** - 1 producto
6. **Puerta Ventana Corrediza A40 Zócalo Alto Abajo** - 1 producto

### **PAÑOS FIJOS:**
1. **Paño Fijo** - 3 productos
2. **paño fijo rotonda 640** - 2 productos
3. **Paño fijo Modena** - 1 producto
4. **Paño Fijo A40** - 1 producto
5. **Paño fijo rotonda 640 IRREGULAR** - 1 producto

### **OTROS TIPOS:**
1. **Banderola** - 3 productos
2. **Oscilobatiente** - 3 productos
3. **Desplazable** - 2 productos
4. **Tapajuntas** - 4 productos
5. **Premarcos** - 2 productos
6. **Ventiluz** - 2 productos
7. **Proyectante** - 1 producto
8. **Mampara** - 1 producto
9. **Postigo de abrir** - 1 producto

---

## 🏭 LÍNEAS DE PRODUCTOS IDENTIFICADAS

### **LÍNEA A30:**
- Ventana de abrir A30
- Ventana Corrediza A30
- Puerta de Abrir A30
- Tapajuntas A30

### **LÍNEA A40:**
- Ventana de abrir A40
- Paño Fijo A40
- Premarco A40
- Ventana Desplazable A40
- Ventana Banderola A40
- Puerta Ventana Corrediza A40

### **LÍNEA MODENA:**
- Puerta de abrir Modena
- Ventana de abrir Modena Doble Contacto
- Ventana Banderola Modena
- Ventana corrediza 90º Módena
- Paño fijo Modena
- Ventana Desplazable Módena
- Premarco Modena

### **LÍNEA ROTONDA 640:**
- Ventana Oscilobatiente Rotonda 640
- paño fijo rotonda 640
- Puerta de rebatir Rotonda 640
- Ventana proyectante Rotonda 640
- Ventana corrediza de 3 guias Rotonda 640
- Tapajuntas Rotonda 640
- Paño fijo rotonda 640 IRREGULAR
- Ventana corrediza rotonda 640

### **LÍNEA HERRERO:**
- Mampara corrediza Herrero

### **LÍNEA HYDRO:**
- Premarco Hydro

---

## 🔧 COMPONENTES Y CONFIGURACIONES

### **MARCOS IDENTIFICADOS:**
- Códigos como: 02851, 02855, 02856, 02850, 02830, 02891, 02890, 02897
- Total: 229 configuraciones de marco

### **TIPOS DE HOJA:**
- Curvo (de clipar)
- Configuraciones numéricas (1, 3, 5)
- Total: 421 configuraciones

### **TIPOS DE INTERIOR:**
- **VS** (Vidrio Simple)
- **DVH** (Doble Vidriado Hermético)
- Total: 480 configuraciones

---

## 📋 PLANTILLAS PRINCIPALES PARA IMPLEMENTAR

### **VENTANAS (12 plantillas principales):**
1. Ventana de Abrir (A30, A40, Modena)
2. Ventana Corrediza (A30, 90º, 3 hojas)
3. Ventana Oscilobatiente (Rotonda 640)
4. Ventana Banderola (Modena, A40)
5. Ventana Desplazable (Modena, A40)
6. Ventana Proyectante (Rotonda 640)

### **PUERTAS (6 plantillas principales):**
1. Puerta de Abrir (A30, Modena)
2. Puerta de Rebatir (Rotonda 640)
3. Puerta Placa
4. Puerta Ventana Corrediza (A40)

### **PAÑOS FIJOS (5 plantillas):**
1. Paño Fijo estándar
2. Paño Fijo Modena
3. Paño Fijo A40
4. Paño Fijo Rotonda 640
5. Paño Fijo Irregular

### **ACCESORIOS (6 plantillas):**
1. Tapajuntas (A30, Rotonda 640)
2. Premarcos (Modena, A40, Hydro)
3. Ventiluz
4. Postigo
5. Mampara (Herrero)

---

## ✅ CONCLUSIÓN

**TIENES UN SISTEMA COMPLETO CON:**
- **4 líneas principales** (A30, A40, Modena, Rotonda 640)
- **6 categorías** de productos (Ventanas, Puertas, Paños Fijos, etc.)
- **Estructura jerárquica** bien definida
- **Componentes opcionales** (contravidrios, mosquiteros, etc.)

**PRÓXIMO PASO:** Migrar estas plantillas del sistema antiguo al nuevo sistema Django usando `catalog_producttemplate`.