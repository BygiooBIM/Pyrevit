# -*- coding: utf-8 -*-
"""Plantilla de botón BygiooBIM. Reemplaza esta descripción."""
from pyrevit import revit, DB, forms, script
import bim_utils

doc = revit.doc
output = script.get_output()

# 1. Recolectar (solo lectura)
elementos = []

if not elementos:
    forms.alert(u"No se encontró nada que procesar.", exitscript=True)

# 2. Confirmar
opcion = forms.alert(
    u"Se procesarán {} elementos.".format(len(elementos)),
    options=[u"Procesar", u"Cancelar"],
)
if opcion != u"Procesar":
    script.exit()

# 3. Modificar
ok, errores = 0, []
with revit.Transaction(u"Nombre de la acción"):
    for el in elementos:
        try:
            # ... cambio ...
            ok += 1
        except Exception as ex:
            errores.append([output.linkify(el.Id), str(ex)])

# 4. Reportar
output.print_md(u"## Resultado: {} correctos, {} con error".format(ok, len(errores)))
if errores:
    output.print_table(errores, columns=[u"Elemento", u"Error"])
