# 🎯 PLANTILLAS CON FILTRADO REAL POR RELACIONES

## ⚠️ **IMPORTANTE: FILTRADO POR RELACIONES**

**NO todos los marcos van con todas las hojas**  
**NO todas las hojas van con todos los interiores**  
**Los componentes opcionales dependen del interior/hoja específica**

---

## 🚪 **PLANTILLA: VENTANA**

### **ATRIBUTOS CON FILTRADO:**

#### 1. **línea**: SELECT (obligatorio)
- A30, A40, Modena, Rotonda 640

#### 2. **tipo_apertura**: SELECT (obligatorio)  
- Abrir, Corrediza, Oscilobatiente, Banderola, Desplazable, Proyectante

#### 3. **marco**: SELECT (obligatorio) - **FILTRADO POR LÍNEA**
**Ejemplo A30:**
- 6036-6037 (corrediza)
- Borde Recto Hoja Escalonada (abrir)

**Ejemplo Modena:**
- 6216 (abrir doble contacto)
- 6200, 6201 (corrediza 90º)

#### 4. **hoja**: SELECT (obligatorio) - **FILTRADO POR MARCO**
**Ejemplo Marco "6036-6037":**
- DVH
- *T  
- *TR

**Ejemplo Marco "Borde Recto Hoja Escalonada":**
- Borde Recto
- Hoja de Puerta

#### 5. **interior**: SELECT (obligatorio) - **FILTRADO POR HOJA**
**Ejemplo Hoja "DVH":**
- Interior

**Ejemplo Hoja "Borde Recto":**
- Interior normal

#### 6. **dimensiones**: DIMENSIONS_MM (obligatorio)
- min_width: 300mm, max_width: 3000mm
- min_height: 400mm, max_height: 2500mm

#### 7. **cantidad**: QUANTITY (obligatorio)
- min: 1, max: 100

#### 8. **contravidrio**: BOOLEAN (opcional) - **FILTRADO POR INTERIOR**
- Solo disponible si el interior específico tiene contravidrios
- Ejemplo: Interior "DVH" → 6 opciones de contravidrio
- Ejemplo: Interior "Interior normal" → 4 opciones de contravidrio

#### 9. **mosquitero**: BOOLEAN (opcional) - **FILTRADO POR HOJA**
- Solo disponible si la hoja específica tiene mosquiteros
- Ejemplo: Hoja "DVH" → 3 mosquiteros
- Ejemplo: Hoja "Borde Recto" → 2 mosquiteros

#### 10. **vidrio_repartido**: BOOLEAN (opcional) - **FILTRADO POR INTERIOR**
- Solo disponible si el interior específico tiene vidrios repartidos
- Ejemplo: Interior "Interior normal" → 4 opciones

---

## 🚪 **PLANTILLA: PUERTA**

### **RELACIONES ESPECÍFICAS IDENTIFICADAS:**

#### **Marco → Hoja → Interior (ejemplos reales):**
- Marco "6259 (Marco Puerta Placa)" → Hoja "Hoja con 6214" → Interior "Revestimiento"
- Marco "Borde Recto Hoja Escalonada" → Hoja "Hoja de Puerta" → Interior "*TR"

### **ATRIBUTOS CON FILTRADO:**
1. **línea**: SELECT → A30, A40, Modena, Rotonda 640
2. **tipo_apertura**: SELECT → Abrir, Rebatir, Corrediza, Placa
3. **marco**: SELECT (filtrado por línea)
4. **hoja**: SELECT (filtrado por marco)
5. **interior**: SELECT (filtrado por hoja)
6. **dimensiones**: DIMENSIONS_MM
7. **cantidad**: QUANTITY
8. **contravidrio**: BOOLEAN (filtrado por interior)
9. **mosquitero**: BOOLEAN (filtrado por hoja)

---

## 🔲 **PLANTILLA: PAÑO_FIJO**

### **RELACIONES ESPECÍFICAS:**
- Marco "02855" → Hoja "Curvo (de clipar)" → Interior "VS" o "DVH"
- Marco "02856 - NC" → Hoja "Curvo (de clipar)" → Interior "VS" o "DVH"

### **ATRIBUTOS CON FILTRADO:**
1. **línea**: SELECT → A30, A40, Modena, Rotonda 640
2. **marco**: SELECT (filtrado por línea)
3. **hoja**: SELECT (filtrado por marco)
4. **interior**: SELECT (filtrado por hoja)
5. **forma**: SELECT → Regular, Irregular
6. **dimensiones**: DIMENSIONS_MM
7. **cantidad**: QUANTITY

---

## 🔧 **PLANTILLA: ACCESORIO**

### **ATRIBUTOS CON FILTRADO:**
1. **tipo**: SELECT → Tapajuntas, Premarcos, Ventiluz, Postigo, Mampara
2. **línea**: SELECT (filtrado por tipo)
3. **aplicacion**: SELECT → Para Ventana, Para Puerta
4. **marco**: SELECT (filtrado por línea + aplicación)
5. **dimensiones**: DIMENSIONS_MM (opcional)
6. **cantidad**: QUANTITY

---

## 📊 **EJEMPLOS DE FILTRADO REAL**

### **EJEMPLO 1: Ventana A30**
```
Usuario selecciona:
├─ línea: "A30"
├─ tipo_apertura: "Corrediza"
└─ marco: FILTRADO → Solo "6036-6037"

Usuario selecciona marco "6036-6037":
└─ hoja: FILTRADO → Solo "DVH", "*T", "*TR"

Usuario selecciona hoja "DVH":
└─ interior: FILTRADO → Solo "Interior"

Usuario selecciona interior "Interior":
├─ contravidrio: DISPONIBLE (tiene opciones)
├─ mosquitero: DISPONIBLE (hoja DVH tiene 3 opciones)
└─ vidrio_repartido: NO DISPONIBLE
```

### **EJEMPLO 2: Banderola**
```
Usuario selecciona:
├─ tipo_apertura: "Banderola"
└─ marco: FILTRADO → "*TRIA", "03102 - NC", "06418", etc.

Usuario selecciona marco "*TRIA":
└─ hoja: FILTRADO → "03019 VS", "03048 DVH", "02822", "*TRIA"

Usuario selecciona hoja "03048 DVH":
└─ interior: FILTRADO → "DVH"

Usuario selecciona interior "DVH":
├─ contravidrio: DISPONIBLE (6 opciones)
└─ mosquitero: VERIFICAR por hoja específica
```

---

## ⚡ **IMPLEMENTACIÓN TÉCNICA**

### **Reglas de Filtrado:**
1. **Cascada obligatoria**: línea → marco → hoja → interior
2. **Componentes opcionales**: Verificar disponibilidad por interior/hoja
3. **Cache de relaciones**: Pre-cargar mapeos para performance
4. **Validación**: Verificar que la combinación existe en BD

### **Estructura de Datos:**
```json
{
  "linea_A30": {
    "marcos": {
      "6036-6037": {
        "hojas": {
          "DVH": ["Interior"],
          "*T": ["Int"],
          "*TR": ["Interior", "Interior 3 Hojas"]
        }
      }
    }
  }
}
```

---

## ✅ **CONCLUSIÓN**

**FILTRADO REAL IDENTIFICADO:**
- **229 marcos** → Cada uno con hojas específicas
- **421 hojas** → Cada una con interiores específicos  
- **480 interiores** → Cada uno con componentes opcionales específicos

**PRÓXIMO PASO:** Implementar sistema de filtrado dinámico en Django que respete estas relaciones reales.