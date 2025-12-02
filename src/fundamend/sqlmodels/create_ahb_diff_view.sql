-- Assume that materialize_ahb_view.sql has been executed already.
-- This view allows comparing two AHB versions to find added, deleted, and modified rows.
-- Usage:
--   SELECT * FROM v_ahb_diff
--   WHERE format_version_a = 'FV2504'
--     AND format_version_b = 'FV2410'
--     AND pruefidentifikator_a = '55014'
--     AND pruefidentifikator_b = '55014'
--     AND diff_status = 'added'
--   ORDER BY sort_path;
--
-- diff_status can be: 'added', 'deleted', 'modified', 'unchanged'

DROP TABLE IF EXISTS v_ahb_diff;
DROP VIEW IF EXISTS v_ahb_diff;

CREATE VIEW v_ahb_diff AS
-- Rows in A (added, modified, unchanged)
SELECT a.edifact_format_version           as format_version_a,
       b.edifact_format_version           as format_version_b,
       a.pruefidentifikator               as pruefidentifikator_a,
       b.pruefidentifikator               as pruefidentifikator_b,
       COALESCE(a.path, b.path)           as path,
       COALESCE(a.id_path, b.id_path)     as id_path,
       COALESCE(a.sort_path, b.sort_path) as sort_path,
       COALESCE(a.type, b.type)           as type,
       -- Segment Group
       a.segmentgroup_name                as segmentgroup_name_a,
       b.segmentgroup_name                as segmentgroup_name_b,
       a.segmentgroup_ahb_status          as segmentgroup_ahb_status_a,
       b.segmentgroup_ahb_status          as segmentgroup_ahb_status_b,
       -- Segment
       a.segment_id                       as segment_id_a,
       b.segment_id                       as segment_id_b,
       a.segment_name                     as segment_name_a,
       b.segment_name                     as segment_name_b,
       a.segment_ahb_status               as segment_ahb_status_a,
       b.segment_ahb_status               as segment_ahb_status_b,
       -- Data Element Group
       a.dataelementgroup_id              as dataelementgroup_id_a,
       b.dataelementgroup_id              as dataelementgroup_id_b,
       a.dataelementgroup_name            as dataelementgroup_name_a,
       b.dataelementgroup_name            as dataelementgroup_name_b,
       -- Data Element
       a.dataelement_id                   as dataelement_id_a,
       b.dataelement_id                   as dataelement_id_b,
       a.dataelement_name                 as dataelement_name_a,
       b.dataelement_name                 as dataelement_name_b,
       a.dataelement_ahb_status           as dataelement_ahb_status_a,
       b.dataelement_ahb_status           as dataelement_ahb_status_b,
       -- Code
       a.code_value                       as code_value_a,
       b.code_value                       as code_value_b,
       a.code_name                        as code_name_a,
       b.code_name                        as code_name_b,
       a.code_ahb_status                  as code_ahb_status_a,
       b.code_ahb_status                  as code_ahb_status_b,
       -- Diff status (only compare AHB status fields, not names)
       CASE
           WHEN b.id IS NULL THEN 'added'
           WHEN a.segmentgroup_ahb_status != b.segmentgroup_ahb_status
               OR a.segment_ahb_status != b.segment_ahb_status
               OR a.dataelement_ahb_status != b.dataelement_ahb_status
               OR a.code_ahb_status != b.code_ahb_status
               OR (a.segmentgroup_ahb_status IS NULL) != (b.segmentgroup_ahb_status IS NULL)
               OR (a.segment_ahb_status IS NULL) != (b.segment_ahb_status IS NULL)
               OR (a.dataelement_ahb_status IS NULL) != (b.dataelement_ahb_status IS NULL)
               OR (a.code_ahb_status IS NULL) != (b.code_ahb_status IS NULL)
               THEN 'modified'
           ELSE 'unchanged'
           END                            as diff_status
FROM ahb_hierarchy_materialized a
         LEFT JOIN ahb_hierarchy_materialized b
                   ON a.id_path = b.id_path
                   AND COALESCE(a.segmentgroup_name, '') = COALESCE(b.segmentgroup_name, '')

UNION ALL

-- Rows only in B (deleted)
SELECT a.edifact_format_version  as format_version_a,
       b.edifact_format_version  as format_version_b,
       a.pruefidentifikator      as pruefidentifikator_a,
       b.pruefidentifikator      as pruefidentifikator_b,
       b.path                    as path,
       b.id_path                 as id_path,
       b.sort_path               as sort_path,
       b.type                    as type,
       -- Segment Group
       NULL                      as segmentgroup_name_a,
       b.segmentgroup_name       as segmentgroup_name_b,
       NULL                      as segmentgroup_ahb_status_a,
       b.segmentgroup_ahb_status as segmentgroup_ahb_status_b,
       -- Segment
       NULL                      as segment_id_a,
       b.segment_id              as segment_id_b,
       NULL                      as segment_name_a,
       b.segment_name            as segment_name_b,
       NULL                      as segment_ahb_status_a,
       b.segment_ahb_status      as segment_ahb_status_b,
       -- Data Element Group
       NULL                      as dataelementgroup_id_a,
       b.dataelementgroup_id     as dataelementgroup_id_b,
       NULL                      as dataelementgroup_name_a,
       b.dataelementgroup_name   as dataelementgroup_name_b,
       -- Data Element
       NULL                      as dataelement_id_a,
       b.dataelement_id          as dataelement_id_b,
       NULL                      as dataelement_name_a,
       b.dataelement_name        as dataelement_name_b,
       NULL                      as dataelement_ahb_status_a,
       b.dataelement_ahb_status  as dataelement_ahb_status_b,
       -- Code
       NULL                      as code_value_a,
       b.code_value              as code_value_b,
       NULL                      as code_name_a,
       b.code_name               as code_name_b,
       NULL                      as code_ahb_status_a,
       b.code_ahb_status         as code_ahb_status_b,
       -- Diff status
       'deleted'                 as diff_status
FROM ahb_hierarchy_materialized b
         LEFT JOIN ahb_hierarchy_materialized a
                   ON b.id_path = a.id_path
                   AND COALESCE(b.segmentgroup_name, '') = COALESCE(a.segmentgroup_name, '')
WHERE a.id IS NULL;
