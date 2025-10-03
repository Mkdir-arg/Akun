#!/usr/bin/env python3
"""
Script para corregir problemas de encoding en TemplateList.tsx
"""

import re

def fix_encoding_issues():
    file_path = "src/components/templates/TemplateList.tsx"
    
    # Mapeo de caracteres corruptos a caracteres correctos
    replacements = {
        "ÃƒÆ'Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¿EstÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â¡s seguro": "¿Estás seguro",
        "LÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â­nea": "Línea",
        "lÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â­neas": "líneas",
        "CategorÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â­a": "Categoría",
        "categorÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â­as": "categorías",
        "creaciÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â³n": "creación",
        "selecciÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â³n": "selección",
        "EjecutÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â¡ la sincronizaciÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â³n": "Ejecuta la sincronización",
        "especÃƒÆ'Ã‚Â­ficamente": "específicamente",
        "CÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â³digo": "Código",
        "RelaciÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â³n": "Relación",
        "ÃƒÆ'Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â'": "—",
        "? Volver": "← Volver",
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar reemplazos
        for corrupted, fixed in replacements.items():
            content = content.replace(corrupted, fixed)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Encoding corregido en {file_path}")
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_encoding_issues()