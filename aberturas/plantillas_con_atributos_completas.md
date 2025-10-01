# 🏗️ PLANTILLAS CON ATRIBUTOS Y VALORES COMPLETAS

## 📋 ESTRUCTURA DE PLANTILLAS IDENTIFICADA

### 🚪 **PLANTILLA: VENTANA**

**ATRIBUTOS:**
- **línea**: SELECT (obligatorio)
- **tipo_apertura**: SELECT (obligatorio)
- **marco**: SELECT (obligatorio)
- **hoja**: SELECT (obligatorio)
- **interior**: SELECT (obligatorio)
- **dimensiones**: DIMENSIONS_MM (obligatorio)
- **cantidad**: QUANTITY (obligatorio)
- **contravidrio**: BOOLEAN (opcional)
- **mosquitero**: BOOLEAN (opcional)
- **vidrio_repartido**: BOOLEAN (opcional)
- **cruces**: BOOLEAN (opcional)

**VALORES DISPONIBLES:**

#### **línea** (4 opciones principales):
- A30 (Línea económica)
- A40 (Línea intermedia)
- Modena (Línea premium)
- Rotonda 640 (Línea especializada)

#### **tipo_apertura** (6 opciones):
- Abrir (más común)
- Corrediza (2H, 3H, 4H, 6H)
- Oscilobatiente
- Banderola
- Desplazable
- Proyectante

#### **marco** (por línea):
**A30:**
- Borde Recto Hoja Escalonada
- 6036-6037 (corrediza)
- 6206 (tapajuntas)

**A40:**
- 8342 (banderola)
- 8345 (desplazable)
- 8337, 8338 (varios)

**Modena:**
- 6216 (abrir doble contacto)
- 6200, 6201 (corrediza 90º)
- 6214 (puerta)
- 6259 (puerta placa)

**Rotonda 640:**
- ADR1160, ADR1162, ADR1166
- ADR1512 (proyectante)
- ADR1510 (corrediza)
- ADR2466, ADR1800 (paño fijo)

#### **hoja** (principales):
- Curvo (de clipar)
- Recto (de clipar)
- Recto (de encolizar)
- DVH (Doble Vidriado Hermético)
- VS (Vidrio Simple)
- Hoja Escalonada
- Borde Recto

#### **interior** (3 opciones principales):
- VS (Vidrio Simple)
- DVH (Doble Vidriado Hermético)
- Vidrio repartido

---

### 🚪 **PLANTILLA: PUERTA**

**ATRIBUTOS:**
- **línea**: SELECT (obligatorio)
- **tipo_apertura**: SELECT (obligatorio)
- **marco**: SELECT (obligatorio)
- **hoja**: SELECT (obligatorio)
- **interior**: SELECT (obligatorio)
- **dimensiones**: DIMENSIONS_MM (obligatorio)
- **cantidad**: QUANTITY (obligatorio)
- **contravidrio**: BOOLEAN (opcional)
- **mosquitero**: BOOLEAN (opcional)
- **zocalo**: BOOLEAN (opcional)

**VALORES DISPONIBLES:**

#### **línea** (4 opciones):
- A30, A40, Modena, Rotonda 640

#### **tipo_apertura** (4 opciones):
- Abrir (más común)
- Rebatir
- Corrediza
- Placa

#### **marco** (por línea):
**A30:**
- Borde Recto Hoja Escalonada

**Modena:**
- 6259 (Marco Puerta Placa)
- 6214 (Hoja Puerta)

**Rotonda 640:**
- Marcos específicos ADR

#### **hoja** (principales):
- Hoja de Puerta
- Hoja con 6214
- Hoja Escalonada
- Hoja con 6214 - Doble Zócalo

#### **interior** (opciones):
- Vidrio Simple
- DVH
- Revestimiento
- Revestimiento de tablilla
- Policarbonato/Acrílico

---

### 🔲 **PLANTILLA: PAÑO_FIJO**

**ATRIBUTOS:**
- **línea**: SELECT (obligatorio)
- **marco**: SELECT (obligatorio)
- **interior**: SELECT (obligatorio)
- **dimensiones**: DIMENSIONS_MM (obligatorio)
- **cantidad**: QUANTITY (obligatorio)
- **forma**: SELECT (opcional)

**VALORES DISPONIBLES:**

#### **línea** (4 opciones):
- A30, A40, Modena, Rotonda 640

#### **marco** (por línea):
**Estándar:**
- 02851, 02855, 02856
- 08018, 08102
- 00128, 00107

**Modena:**
- Marco recto con 6216

**A40:**
- Marcos específicos A40

**Rotonda 640:**
- ADR1160, ADR1800, ADR2466

#### **forma** (2 opciones):
- Regular
- Irregular

#### **interior** (3 opciones):
- VS (Vidrio Simple)
- DVH (Doble Vidriado Hermético)
- Vidrio repartido

---

### 🔧 **PLANTILLA: ACCESORIO**

**ATRIBUTOS:**
- **tipo**: SELECT (obligatorio)
- **línea**: SELECT (obligatorio)
- **aplicacion**: SELECT (obligatorio)
- **marco**: SELECT (obligatorio)
- **dimensiones**: DIMENSIONS_MM (opcional)
- **cantidad**: QUANTITY (obligatorio)

**VALORES DISPONIBLES:**

#### **tipo** (6 opciones):
- Tapajuntas
- Premarcos
- Ventiluz
- Postigo
- Mampara
- Marco Combinado

#### **línea** (5 opciones):
- A30, A40, Modena, Rotonda 640, Herrero, Hydro

#### **aplicacion** (2 opciones):
- Para Ventana
- Para Puerta

#### **marco** (por tipo):
**Tapajuntas:**
- 02826, 02892, 09011, 09013
- 08010, 08013, 03024, 03025
- ADR191, ADR62 (Rotonda 640)

**Premarcos:**
- 08029, 08031 (para puerta)
- 6901 (Modena)
- ADR230 (Hydro)

---

## 🎯 **RESUMEN DE ATRIBUTOS COMUNES**

### **ATRIBUTOS OBLIGATORIOS** (todas las plantillas):
1. **dimensiones**: DIMENSIONS_MM
   - min_width: 300mm
   - max_width: 3000mm
   - min_height: 400mm
   - max_height: 2500mm
   - step_mm: 10

2. **cantidad**: QUANTITY
   - min_value: 1
   - max_value: 100
   - step_value: 1

### **ATRIBUTOS ESPECÍFICOS POR CATEGORÍA**:

#### **VENTANAS Y PUERTAS**:
- línea (SELECT)
- tipo_apertura (SELECT)
- marco (SELECT)
- hoja (SELECT)
- interior (SELECT)
- contravidrio (BOOLEAN)
- mosquitero (BOOLEAN)

#### **PAÑOS FIJOS**:
- línea (SELECT)
- marco (SELECT)
- interior (SELECT)
- forma (SELECT)

#### **ACCESORIOS**:
- tipo (SELECT)
- línea (SELECT)
- aplicacion (SELECT)
- marco (SELECT)

---

## 📊 **ESTADÍSTICAS DE VALORES**

- **Líneas disponibles**: 4 principales (A30, A40, Modena, Rotonda 640)
- **Marcos disponibles**: 229 configuraciones únicas
- **Hojas disponibles**: 421 variantes
- **Interiores disponibles**: 480 opciones
- **Tipos de apertura**: 6 principales
- **Accesorios**: 6 categorías principales

**TOTAL DE COMBINACIONES POSIBLES**: ~2.5 millones de configuraciones únicas