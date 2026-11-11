---
name: pyrevit-revit
description: Escribe, corrige y organiza herramientas pyRevit (scripts Python para Autodesk Revit 2026) de la extensión de oficina BygiooBIM. Úsala siempre que el usuario pida automatizar algo en Revit, crear un botón o rutina pyRevit, limpiar o auditar un modelo (warnings, duplicados, parámetros, vistas, planos, familias, worksets), exportar datos de Revit a Excel/CSV, o cuando pegue un error de la consola de pyRevit / Revit API, aunque no diga "pyRevit" explícitamente.
---

# pyRevit para Revit 2026 — extensión de oficina BygiooBIM

El usuario no es programador: es la oficina BIM y prueba cada herramienta dentro de Revit
en Windows. Claude escribe el código pero **no puede ejecutarlo** (no hay Revit en la sesión),
así que el código tiene que ser defensivo, explicar lo que hace en la ventana de salida y
nunca dañar el modelo sin confirmación.

## Dónde vive el código

La raíz del repositorio `BygiooBIM/Pyrevit` **es** la extensión (pyRevit la instala
clonándola como `BygiooBIM.extension`):

```
README.md                     # instalación y lista de herramientas
lib/bim_utils.py              # utilidades compartidas (importar, no duplicar)
BygiooBIM.tab/
└── <Panel>.panel/
    └── <Herramienta>.pushbutton/
        ├── script.py
        ├── bundle.yaml       # título, tooltip, autor
        └── icon.png          # 96x96 PNG (opcional)
```

- Nombres de carpeta en ASCII, sin tildes ni espacios (`Auditoria.panel`, `EliminarDuplicados.pushbutton`);
  el texto visible con tildes va en `bundle.yaml` (`title:`).
- Antes de escribir una herramienta nueva, lee `lib/bim_utils.py` y reutiliza lo que haya.
  Si un helper sirve a 2+ herramientas, muévelo ahí.
- Al terminar, añade la herramienta a la tabla de `README.md`, sube `version.txt`
  (1.0.0 → 1.1.0 si hay herramienta nueva, 1.0.1 si es corrección) y anota el cambio en *Versiones*.
- Para compartir con compañeros, genera el paquete con
  `bash instalador/empaquetar.sh <carpeta_salida>`: crea `BygiooBIM_Instalador_v<versión>.zip`
  con `Instalar_BygiooBIM.bat` + `BygiooBIM.zip`. El `.bat` instala y también actualiza.
- Para crear un botón nuevo copia `assets/pushbutton_template/` y genera el icono con
  `python scripts/make_icon.py <carpeta.pushbutton> "<TEXTO>" "#color"`.

## Reglas del código (por qué importan)

1. **Motor IronPython 2.7 por defecto** (el estándar de pyRevit y el más compatible).
   Nada de f-strings, `print()` con `sep=`, type hints ni `pathlib`. Usa `"{}".format(...)`.
   Primera línea siempre `# -*- coding: utf-8 -*-` y textos en español como `u"..."` cuando
   lleven tildes, o IronPython falla con UnicodeDecodeError.
2. **Revit 2026 eliminó `ElementId.IntegerValue`** (ahora es Int64 y se usa `.Value`).
   Usa siempre `bim_utils.eid_int(eid)` y `DB.ElementId(Int64)` vía `bim_utils.make_eid(n)`.
   Lee `references/revit-2026.md` antes de usar APIs que hayan cambiado.
3. **Toda modificación dentro de una transacción** con nombre en español
   (`with revit.Transaction(u"Eliminar duplicados"):`) — así el usuario la deshace con Ctrl+Z
   en un solo paso. Leer el modelo no necesita transacción.
4. **Confirmar antes de borrar o modificar en lote.** Muestra cuántos elementos se afectarán
   y ofrece "solo seleccionar / solo reportar" como alternativa segura (`forms.alert(..., options=[...])`).
5. **Errores por elemento, no por lote.** Envuelve cada `doc.Delete`/`Set` en `try/except`,
   cuenta fallos y repórtalos al final; un elemento problemático no debe abortar todo.
6. **Respetar trabajo compartido**: no tocar elementos de otro usuario
   (`bim_utils.owned_by_other(doc, eid)`), y avisar de los elementos en grupos o fijados (pinned).
7. **No depender del idioma de Revit.** La oficina puede tener Revit en español o inglés:
   identifica warnings por `BuiltInFailures` (GUID), categorías por `BuiltInCategory`
   y parámetros por `BuiltInParameter` o GUID, nunca por el texto visible.
8. **Reporte claro en la ventana de salida** (`script.get_output()`): resumen al principio,
   tabla con `output.print_table`, y IDs clicables con `output.linkify(eid)` para que el usuario
   pueda saltar al elemento.
9. **Unidades**: la API trabaja en pies internos. Convierte con
   `DB.UnitUtils.ConvertFromInternalUnits(valor, DB.UnitTypeId.Meters)` antes de mostrar.

## Esqueleto de script

```python
# -*- coding: utf-8 -*-
"""Descripción corta (aparece como tooltip si no hay bundle.yaml)."""
from pyrevit import revit, DB, forms, script
import bim_utils

doc = revit.doc
output = script.get_output()

# 1. Recolectar (solo lectura)
# 2. Mostrar resumen y pedir confirmación
# 3. Modificar dentro de revit.Transaction, con try/except por elemento
# 4. Reportar resultados
```

## Cómo entregar cada herramienta al usuario

Responde en español, en este orden:
1. Qué hace la herramienta en 2–3 líneas, y qué **no** hace.
2. Dónde quedó (ruta de la carpeta del botón).
3. Cómo probarla: "pyRevit → Reload", en qué pestaña/panel aparece, y la recomendación de
   probar primero en una copia del modelo.
4. Qué pegarte si falla: el texto completo de la ventana roja de pyRevit.

## Cuando el usuario pega un error

Lee la última línea del traceback (tipo de error) y la línea del script indicada.
Causas frecuentes en este entorno:
- `AttributeError: 'ElementId' object has no attribute 'IntegerValue'` → regla 2.
- `UnicodeDecodeError` / caracteres raros → regla 1.
- `ModificationOutsideTransactionException` → regla 3.
- `InvalidOperationException` al borrar → elemento en grupo, dependiente o de otro usuario.
Corrige, explica la causa en una frase y pide que vuelva a probar.
