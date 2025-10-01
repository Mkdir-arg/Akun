# SISTEMA DE ABERTURAS - AKUN

Sistema completo de gestión de aberturas con plantillas dinámicas y presupuestos.

## 🚀 INICIO RÁPIDO

### **Levantar el sistema:**
```bash
docker compose up --build
```

### **Acceder:**
- **Frontend:** http://localhost:3001/#/login
- **Backend:** http://localhost:8002/admin/

## 🏗️ ARQUITECTURA

- **Frontend:** React + TypeScript (puerto 3001)
- **Backend:** Django + MySQL (puerto 8002)
- **Base de datos:** MySQL local `akun`
- **Cache:** Redis

## 📋 FUNCIONALIDADES

### **Sistema de Plantillas:**
- 111 plantillas base identificadas
- Filtros dinámicos cascada (línea → marco → hoja → interior)
- 4 líneas principales: A30, A40, Modena, Rotonda 640
- Cálculo automático de precios

### **Sistema de Presupuestos:**
- Creación con configuración de plantillas
- Cálculo automático de totales e IVA
- Configuración JSON por ítem
- Integración completa frontend-backend

## 🔧 COMANDOS ÚTILES

### **Ver logs:**
```bash
docker compose logs frontend
docker compose logs backend
```

### **Acceder a contenedores:**
```bash
docker compose exec frontend sh
docker compose exec backend bash
```

### **Backup de datos:**
```bash
docker compose exec backend python create_complete_fixtures.py
```

## 📊 DATOS

- **229 marcos** disponibles
- **421 hojas** configuradas  
- **480 interiores** (VS/DVH)
- **Relaciones jerárquicas** validadas
- **Precios dinámicos** por configuración

## 📁 BACKUP

Todo el análisis y desarrollo está respaldado en:
- `BACKUP_ANALISIS/` - Fixtures y documentación completa
- `BACKUP_SISTEMA_COMPLETO.md` - Resumen técnico completo

---

**Desarrollado para AKUN** - Sistema de gestión de aberturas