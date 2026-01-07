# MIG SQLModels Design

## Overview

Add SQLModel support for Message Implementation Guides (MIGs), mirroring the existing AHB SQLModel implementation. This enables persisting MIG data to SQL databases with the same patterns used for AHBs.

## File Structure

Create new file: `src/fundamend/sqlmodels/messageimplementationguide.py`

## Classes

| SQL Model Class | Pydantic Source | Has `position`? |
|-----------------|-----------------|-----------------|
| `MigCode` | `models.messageimplementationguide.Code` | Yes |
| `MigDataElement` | `models.messageimplementationguide.DataElement` | Yes |
| `MigDataElementGroup` | `models.messageimplementationguide.DataElementGroup` | Yes |
| `MigSegment` | `models.messageimplementationguide.Segment` | Yes |
| `MigSegmentGroupLink` | (artificial join table) | No |
| `MigSegmentGroup` | `models.messageimplementationguide.SegmentGroup` | Yes |
| `MessageImplementationGuide` | `models.messageimplementationguide.MessageImplementationGuide` | No |

## Field Mappings

### MigCode
- `primary_key: UUID`
- `name: str`
- `description: str | None`
- `value: str | None`
- `position: Optional[int]`
- FK: `data_element_primary_key`

### MigDataElement
- `primary_key: UUID`
- `id: str`
- `name: str`
- `description: str | None`
- `status_std: str` (MigStatus stored as string)
- `status_specification: str`
- `format_std: str`
- `format_specification: str`
- `codes: list[MigCode]`
- `position: Optional[int]`
- FK: `data_element_group_primary_key` (optional)
- FK: `segment_primary_key` (optional)

### MigDataElementGroup
- `primary_key: UUID`
- `id: str`
- `name: str`
- `description: str | None`
- `status_std: str`
- `status_specification: str`
- `data_elements: list[MigDataElement]`
- `position: Optional[int]`
- FK: `segment_primary_key`

### MigSegment
- `primary_key: UUID`
- `id: str`
- `name: str`
- `description: str | None`
- `counter: str`
- `level: int`
- `number: str`
- `max_rep_std: int`
- `max_rep_specification: int`
- `status_std: str`
- `status_specification: str`
- `example: str | None`
- `is_on_uebertragungsdatei_level: bool`
- `data_elements: list[MigDataElement]`
- `data_element_groups: list[MigDataElementGroup]`
- `position: Optional[int]`
- FK: `segmentgroup_primary_key` (optional)
- FK: `mig_primary_key` (optional)

### MigSegmentGroupLink
- `parent_id: UUID` (FK to MigSegmentGroup, PK)
- `child_id: UUID` (FK to MigSegmentGroup, PK)

### MigSegmentGroup
- `primary_key: UUID`
- `id: str`
- `name: str`
- `counter: str`
- `level: int`
- `max_rep_std: int`
- `max_rep_specification: int`
- `status_std: str`
- `status_specification: str`
- `segments: list[MigSegment]`
- `segment_groups: list[MigSegmentGroup]` (via MigSegmentGroupLink)
- `parent_segment_group: MigSegmentGroup | None` (via MigSegmentGroupLink)
- `position: Optional[int]`
- FK: `mig_primary_key` (optional)

### MessageImplementationGuide
- `primary_key: UUID`
- `veroeffentlichungsdatum: date`
- `autor: str`
- `versionsnummer: str`
- `format: EdifactFormat`
- `segments: list[MigSegment]`
- `segment_groups: list[MigSegmentGroup]`
- SQL-only fields:
  - `gueltig_von: Optional[date]`
  - `gueltig_bis: Optional[date]`
  - `edifact_format_version: Optional[EdifactFormatVersion]`

## Relationships

```
MessageImplementationGuide
├── segments: list[MigSegment]          (FK: mig_primary_key)
└── segment_groups: list[MigSegmentGroup]  (FK: mig_primary_key)

MigSegmentGroup
├── segments: list[MigSegment]          (FK: segmentgroup_primary_key)
├── segment_groups: list[MigSegmentGroup]  (via MigSegmentGroupLink)
└── parent_segment_group: MigSegmentGroup  (via MigSegmentGroupLink)

MigSegment
├── data_elements: list[MigDataElement]      (FK: segment_primary_key)
└── data_element_groups: list[MigDataElementGroup]  (FK: segment_primary_key)

MigDataElementGroup
└── data_elements: list[MigDataElement]  (FK: data_element_group_primary_key)

MigDataElement
└── codes: list[MigCode]  (FK: data_element_primary_key)
```

## UniqueConstraints

Following AHB pattern - position unique within parent:
- `MigCode`: `(data_element_primary_key, position)`
- `MigDataElementGroup`: `(segment_primary_key, position)`
- `MigSegment`: position unique per parent (MIG or SegmentGroup) - separate constraints
- `MigSegmentGroup`: `(mig_primary_key, position)`

## Conversion Logic

### `from_model()` pattern
- Classmethod taking Pydantic model + optional `position` parameter
- Direct field mappings
- Enumerate children to get position index
- Use `isinstance` checks for union types to route to correct list

### `to_model()` pattern
- Instance method returning Pydantic model
- Merge union-type lists, sort by `position`
- Return `tuple()` for Pydantic tuple fields
- MigStatus enum restored via Pydantic validation

## Exports

Update `sqlmodels/__init__.py`:
```python
from .messageimplementationguide import (
    MigCode,
    MigDataElement,
    MigDataElementGroup,
    MigSegment,
    MigSegmentGroup,
    MessageImplementationGuide,
)
```

## Testing

New file: `unittests/test_sqlmodels_messageimplementationguide.py`

Tests:
1. Single MIG roundtrip: XML → Pydantic → SQL → Pydantic → compare equality
2. All MIGs from private submodule (skip if not checked out)

Reuse `sqlite_session` fixture from conftest.

## Future Work (out of scope)

- `MigHierarchyMaterialized` view for flattening
- Prefix AHB classes (`AhbCode`, `AhbDataElement`, etc.) for consistency
