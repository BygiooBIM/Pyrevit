# BygiooBIM — extensión pyRevit (Revit 2026)

Herramientas de la oficina para Revit 2026. Se requiere pyRevit 5.x.
La raíz de este repositorio es la extensión: pyRevit la instala como `BygiooBIM.extension`.

## Instalación rápida (para compañeros)

1. Descarga y descomprime el paquete `BygiooBIM_Instalador_vX.zip`.
2. Doble clic en **`Instalar_BygiooBIM.bat`**. Instala en `C:\Autodesk\Extensiones\BygiooBIM.extension`
   y registra la carpeta en pyRevit. Requisito: tener pyRevit 5.x instalado.
3. Abre Revit 2026 (o **pyRevit → Reload**). Aparece la pestaña **BygiooBIM**.

**Para actualizar:** ejecuta de nuevo el `.bat` (con el paquete nuevo junto a él, o sin ZIP para
descargar la última versión de GitHub si el repositorio es público). Después, **pyRevit → Reload**.

Versión instalada: archivo `version.txt`. Cambios por versión: sección *Versiones* al final.

## Instalación alternativa

### Opción A: desde GitHub (recomendada, permite actualizar con un clic)
Abre una terminal (cmd) en Windows y ejecuta:

```
pyrevit extend ui BygiooBIM https://github.com/BygiooBIM/Pyrevit.git --branch=main
```

El `--branch=main` es necesario: pyRevit busca por defecto la rama `master`.
Si el repositorio es privado, agrega `--username TU_USUARIO --password TU_TOKEN`
(el token es un *personal access token* de GitHub con permiso de lectura).

Luego, en Revit: **pyRevit → Reload**. Aparece la pestaña **BygiooBIM**.
Para actualizar: **pyRevit → Update**, o en la terminal `pyrevit extensions update BygiooBIM`.

### Opción B: manual (ZIP)
1. **Code → Download ZIP** y descomprime en, por ejemplo, `C:\BIM\Extensiones\`.
2. Renombra la carpeta descomprimida (`Pyrevit-main`) a **`BygiooBIM.extension`**.
3. En Revit: **pyRevit → Settings → Custom Extension Directories → Add folder** → `C:\BIM\Extensiones`
   (la carpeta que *contiene* `BygiooBIM.extension`) → **Save Settings and Reload**.

## Herramientas

| Panel     | Botón               | Qué hace |
|-----------|---------------------|----------|
| Auditoria | Eliminar Duplicados | Lee el warning "Hay instancias idénticas en el mismo lugar", conserva una instancia por grupo y elimina las demás. Muestra un reporte antes de borrar y ofrece la opción "Solo seleccionarlos". Se deshace con Ctrl+Z. No borra elementos que estén en grupos, que tengan puertas o ventanas alojadas o que pertenezcan a otro usuario: esos quedan en el reporte para revisarlos a mano. |

## Si algo falla

Copia el texto completo de la ventana roja de pyRevit y pégaselo a Claude.

## Para Claude

Las reglas de desarrollo están en la skill `.claude/skills/pyrevit-revit/SKILL.md`.

## Versiones

- **1.0.0** — Primera versión: Auditoria → Eliminar Duplicados. Instalador `.bat`.
