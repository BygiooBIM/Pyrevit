# -*- coding: utf-8 -*-
"""Utilidades compartidas de la extensión BygiooBIM (Revit 2026 / pyRevit).

pyRevit agrega automáticamente la carpeta lib/ de la extensión al path,
así que cualquier botón puede hacer `import bim_utils`.
"""
import System
from Autodesk.Revit import DB


def eid_int(eid):
    """Número de un ElementId. Revit 2024+ usa .Value (Int64); 2026 ya no tiene IntegerValue."""
    if eid is None:
        return -1
    try:
        return int(eid.Value)
    except AttributeError:  # Revit 2023 o anterior
        return int(eid.IntegerValue)


def make_eid(number):
    """Crea un ElementId a partir de un número (Revit 2026 requiere Int64)."""
    return DB.ElementId(System.Int64(int(number)))


def owned_by_other(doc, eid):
    """True si el elemento está tomado por otro usuario en un modelo compartido."""
    if not doc.IsWorkshared:
        return False
    try:
        status = DB.WorksharingUtils.GetCheckoutStatus(doc, eid)
        return status == DB.CheckoutStatus.OwnedByOtherUser
    except Exception:
        return False


def in_group(element):
    """True si el elemento pertenece a un grupo de modelo/detalle."""
    gid = getattr(element, "GroupId", None)
    return gid is not None and gid != DB.ElementId.InvalidElementId


def hosted_elements(doc, element):
    """Ids de las familias alojadas en el elemento (puertas en un muro, etc.)."""
    result = []
    try:
        deps = element.GetDependentElements(DB.ElementClassFilter(DB.FamilyInstance))
    except Exception:
        return result
    for dep_id in deps:
        dep = doc.GetElement(dep_id)
        host = getattr(dep, "Host", None)
        if host is not None and host.Id == element.Id:
            result.append(dep_id)
    return result


def element_label(element):
    """Texto legible 'Familia: Tipo' sin depender del idioma de Revit."""
    try:
        if isinstance(element, DB.FamilyInstance):
            return u"{}: {}".format(element.Symbol.Family.Name, element.Symbol.Name)
        type_el = element.Document.GetElement(element.GetTypeId())
        if type_el is not None:
            fam = getattr(type_el, "FamilyName", u"") or u""
            name = DB.Element.Name.GetValue(type_el)
            return u"{}: {}".format(fam, name) if fam else name
        return DB.Element.Name.GetValue(element)
    except Exception:
        return u"(sin nombre)"


def category_name(element):
    cat = element.Category
    return cat.Name if cat is not None else u"(sin categoría)"
