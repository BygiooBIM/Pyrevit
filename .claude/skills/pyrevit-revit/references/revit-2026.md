# Notas de API para Revit 2026 + pyRevit

## Cambios que rompen scripts antiguos

| Antes (≤2023)                         | Revit 2026                                   |
|---------------------------------------|----------------------------------------------|
| `eid.IntegerValue` (Int32)            | `eid.Value` (Int64). `IntegerValue` ya no existe. |
| `DB.ElementId(int)`                   | `DB.ElementId(System.Int64(n))`              |
| `DisplayUnitType`, `UnitType`         | `UnitTypeId`, `SpecTypeId` (ForgeTypeId)     |
| `ParameterType`                       | `param.Definition.GetDataType()` (ForgeTypeId) |
| `BuiltInParameterGroup`               | `GroupTypeId`                                |
| .NET Framework 4.8                    | .NET 8 (desde Revit 2025): requiere pyRevit 5.x |

Los ejemplos de foros y del blog de pyRevit suelen ser antiguos: tradúcelos con esta tabla.

## Warnings (FailureMessage)

```python
for w in doc.GetWarnings():                     # IList<FailureMessage>
    fid = w.GetFailureDefinitionId()            # comparar por .Guid
    ids = w.GetFailingElements()                # elementos principales
    extra = w.GetAdditionalElements()           # a veces también relevantes
    texto = w.GetDescriptionText()              # depende del idioma: solo para mostrar
```

GUIDs útiles en `DB.BuiltInFailures`:
- `OverlapFailures.DuplicateInstances` — "Hay instancias idénticas en el mismo lugar".
- `OverlapFailures.WallsOverlap` — muros superpuestos (no se deben borrar automáticamente).
- `OverlapFailures.RoomSeparationLinesOverlap`, `OverlapFailures.LinesOverlap`.
- `RoomFailures.RoomNotEnclosed`, `RoomFailures.RoomsInSameRegion`.

Compara así: `fid.Guid == DB.BuiltInFailures.OverlapFailures.DuplicateInstances.Guid`.

## Trabajo compartido

```python
if doc.IsWorkshared:
    st = DB.WorksharingUtils.GetCheckoutStatus(doc, eid)
    # DB.CheckoutStatus.OwnedByOtherUser -> no tocar
```

## Selección en la interfaz

```python
from System.Collections.Generic import List
revit.uidoc.Selection.SetElementIds(List[DB.ElementId](ids))
# o simplemente: revit.get_selection().set_to(ids)
```

## pyRevit forms más usados

- `forms.alert(msg, title=..., options=["A", "B"])` → devuelve el texto elegido o None.
- `forms.SelectFromList.show(items, multiselect=True, title=...)`
- `forms.ask_for_string(default=..., prompt=...)`
- `forms.pick_file(file_ext="xlsx")`, `forms.save_file(file_ext="csv")`
- `forms.ProgressBar(title=..., cancellable=True)` con `pb.update_progress(i, total)`.
