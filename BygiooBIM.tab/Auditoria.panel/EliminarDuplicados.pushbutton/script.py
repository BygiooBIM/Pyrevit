# -*- coding: utf-8 -*-
"""Elimina las instancias duplicadas que Revit reporta en el warning
"Hay instancias idénticas en el mismo lugar" (Identical instances in the same place).

En cada grupo de duplicados conserva una instancia y elimina las demás.
Se conserva, por orden de preferencia: la que está en un grupo de modelo,
la que está fijada (pinned), la que tiene elementos alojados y, si no, la más antigua.
"""
from pyrevit import revit, DB, forms, script
import bim_utils

doc = revit.doc
output = script.get_output()

DUPLICATE_GUID = DB.BuiltInFailures.OverlapFailures.DuplicateInstances.Guid


def duplicate_warnings(document):
    """Warnings de instancias duplicadas, detectados por GUID (vale para Revit en cualquier idioma)."""
    return [w for w in document.GetWarnings()
            if w.GetFailureDefinitionId().Guid == DUPLICATE_GUID]


def build_groups(warnings):
    """Une los elementos de todos los warnings en grupos de duplicados.

    Un mismo elemento puede aparecer en varios warnings (3+ copias en el mismo lugar),
    así que se unen con union-find para no conservar ni borrar dos veces.
    """
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for w in warnings:
        ids = [bim_utils.eid_int(i) for i in w.GetFailingElements()]
        for n in ids:
            parent.setdefault(n, n)
        for n in ids[1:]:
            ra, rb = find(ids[0]), find(n)
            if ra != rb:
                parent[rb] = ra

    groups = {}
    for n in parent:
        groups.setdefault(find(n), []).append(n)
    return [sorted(g) for g in groups.values() if len(g) > 1]


def keeper_priority(element):
    """Menor = preferido para conservar."""
    return (
        0 if bim_utils.in_group(element) else 1,
        0 if element.Pinned else 1,
        0 if bim_utils.hosted_elements(doc, element) else 1,
        bim_utils.eid_int(element.Id),
    )


def plan_group(numbers):
    """Decide qué se conserva y qué se elimina en un grupo. Devuelve (keeper, borrar, saltados)."""
    elements = [doc.GetElement(bim_utils.make_eid(n)) for n in numbers]
    elements = [e for e in elements if e is not None]
    if len(elements) < 2:
        return None, [], []
    elements.sort(key=keeper_priority)
    keeper, to_delete, skipped = elements[0], [], []
    for el in elements[1:]:
        if bim_utils.in_group(el):
            skipped.append((el, u"Está dentro de un grupo"))
        elif bim_utils.owned_by_other(doc, el.Id):
            skipped.append((el, u"Tomado por otro usuario"))
        elif bim_utils.hosted_elements(doc, el):
            skipped.append((el, u"Tiene elementos alojados (puertas/ventanas)"))
        else:
            to_delete.append(el)
    return keeper, to_delete, skipped


# ---------------------------------------------------------------- 1. Recolectar
warnings = duplicate_warnings(doc)
if not warnings:
    forms.alert(u"El modelo no tiene warnings de instancias duplicadas. ¡Todo limpio!",
                title=u"Eliminar duplicados", exitscript=True)

plans = []
for numbers in build_groups(warnings):
    keeper, to_delete, skipped = plan_group(numbers)
    if keeper is not None:
        plans.append((keeper, to_delete, skipped))

delete_ids = [el.Id for _, dels, _ in plans for el in dels]
skipped_all = [(el, why) for _, _, sk in plans for el, why in sk]

# ---------------------------------------------------------------- 2. Mostrar y confirmar
output.print_md(u"# Instancias duplicadas")
output.print_md(u"**{}** warnings · **{}** grupos · **{}** para eliminar · **{}** para revisar a mano".format(
    len(warnings), len(plans), len(delete_ids), len(skipped_all)))

rows = []
for i, (keeper, dels, skipped) in enumerate(plans, 1):
    rows.append([
        i,
        bim_utils.category_name(keeper),
        bim_utils.element_label(keeper),
        output.linkify(keeper.Id),
        output.linkify([e.Id for e in dels]) if dels else u"—",
        u"; ".join(u"{} ({})".format(bim_utils.eid_int(e.Id), why) for e, why in skipped),
    ])
output.print_table(rows, columns=[u"#", u"Categoría", u"Familia: Tipo",
                                  u"Se conserva", u"Se elimina", u"Revisar a mano"])

if not delete_ids:
    forms.alert(u"Hay duplicados, pero ninguno se puede eliminar automáticamente.\n"
                u"Revisa la columna 'Revisar a mano' en la ventana de salida.",
                title=u"Eliminar duplicados", exitscript=True)

choice = forms.alert(
    u"Se encontraron {} instancias duplicadas para eliminar en {} grupos.\n\n"
    u"Se conserva una instancia por grupo. Puedes deshacer con Ctrl+Z.".format(
        len(delete_ids), len(plans)),
    title=u"Eliminar duplicados",
    options=[u"Eliminar duplicados", u"Solo seleccionarlos", u"Cancelar"],
)

if choice == u"Solo seleccionarlos":
    revit.get_selection().set_to(delete_ids)
    output.print_md(u"**{} elementos seleccionados.** No se eliminó nada.".format(len(delete_ids)))
    script.exit()
if choice != u"Eliminar duplicados":
    script.exit()

# ---------------------------------------------------------------- 3. Eliminar
deleted, errors = 0, []
with revit.Transaction(u"Eliminar instancias duplicadas"):
    for eid in delete_ids:
        if doc.GetElement(eid) is None:  # ya se borró junto con otro elemento
            continue
        try:
            doc.Delete(eid)
            deleted += 1
        except Exception as ex:
            errors.append([bim_utils.eid_int(eid), getattr(ex, "Message", None) or repr(ex)])

# ---------------------------------------------------------------- 4. Reportar
remaining = len(duplicate_warnings(doc))
output.print_md(u"## Resultado")
output.print_md(u"- Eliminados: **{}**\n- Con error: **{}**\n- Warnings de duplicados restantes: **{}**".format(
    deleted, len(errors), remaining))
if errors:
    output.print_table(errors, columns=[u"Id", u"Error"])
