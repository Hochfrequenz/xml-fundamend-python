-- Assume that materialize_mig_view.sql has been executed already.
-- This view allows comparing two MIG versions to find added, deleted, and modified rows.
--
-- IMPORTANT: This view produces a cross-product of all version pairs. You MUST filter by version and format.
--
-- Usage for comparing FV2410 -> FV2504 for UTILTS format:
--   SELECT * FROM v_mig_diff
--   WHERE old_format_version = 'FV2410'
--     AND old_format = 'UTILTS'
--     AND new_format_version = 'FV2504'
--     AND new_format = 'UTILTS'
--   ORDER BY sort_path;
--
-- diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
-- The view compares line_status_std, line_status_specification, and line_name to determine modifications.
--
-- For deleted rows, old_ columns are populated and new_ columns are NULL.
-- For added rows, new_ columns are populated and old_ columns are NULL.
--
-- MATCHING STRATEGY:
-- Unlike AHBs (which have Prüfidentifikatoren as stable semantic anchors), MIGs represent the complete
-- message structure without such anchors. This view matches rows by their human-readable 'path' column
-- (e.g., "Nachrichten-Kopfsegment > Nachrichten-Kennung > ...") rather than structural id_path.
-- This provides more semantically meaningful comparisons but has limitations:
-- - If an element is renamed between versions, it appears as added+deleted rather than modified
-- - Elements with identical names at different structural positions may be incorrectly matched
-- For structural comparisons, use id_path directly from mig_hierarchy_materialized.

DROP TABLE IF EXISTS v_mig_diff;
DROP VIEW IF EXISTS v_mig_diff;

CREATE VIEW v_mig_diff AS
WITH version_pairs AS (SELECT DISTINCT old_v.edifact_format_version AS old_format_version,
                                       old_v.format                 AS old_format,
                                       new_v.edifact_format_version AS new_format_version,
                                       new_v.format                 AS new_format
                       FROM (SELECT DISTINCT edifact_format_version, format FROM mig_hierarchy_materialized) old_v
                                JOIN (SELECT DISTINCT edifact_format_version, format
                                      FROM mig_hierarchy_materialized) new_v
                                     ON old_v.format = new_v.format
                       WHERE old_v.edifact_format_version < new_v.edifact_format_version),

-- Pre-compute changed_columns once, derive diff_status from it
     modified_check AS (SELECT TRIM(
                                       CASE
                                           WHEN old_tbl.line_status_std IS NOT new_tbl.line_status_std
                                               THEN 'line_status_std, '
                                           ELSE '' END ||
                                       CASE
                                           WHEN old_tbl.line_status_specification IS NOT new_tbl.line_status_specification
                                               THEN 'line_status_specification, '
                                           ELSE '' END ||
                                       CASE
                                           WHEN old_tbl.line_name IS NOT new_tbl.line_name
                                               THEN 'line_name'
                                           ELSE '' END
                                   , ', ')                       AS changed_columns,
                               new_tbl.id_path                   AS id_path,
                               new_tbl.sort_path                 AS sort_path,
                               new_tbl.path                      AS path,
                               new_tbl.type                      AS line_type,
                               old_tbl.edifact_format_version    AS old_format_version,
                               old_tbl.format                    AS old_format,
                               old_tbl.segmentgroup_id           AS old_segmentgroup_id,
                               old_tbl.segment_id                AS old_segment_id,
                               old_tbl.dataelement_id            AS old_dataelement_id,
                               old_tbl.code_value                AS old_code_value,
                               old_tbl.line_status_std           AS old_line_status_std,
                               old_tbl.line_status_specification AS old_line_status_specification,
                               old_tbl.line_name                 AS old_line_name,
                               new_tbl.edifact_format_version    AS new_format_version,
                               new_tbl.format                    AS new_format,
                               new_tbl.segmentgroup_id           AS new_segmentgroup_id,
                               new_tbl.segment_id                AS new_segment_id,
                               new_tbl.dataelement_id            AS new_dataelement_id,
                               new_tbl.code_value                AS new_code_value,
                               new_tbl.line_status_std           AS new_line_status_std,
                               new_tbl.line_status_specification AS new_line_status_specification,
                               new_tbl.line_name                 AS new_line_name
                        FROM version_pairs vp
                                 JOIN mig_hierarchy_materialized new_tbl
                                      ON new_tbl.edifact_format_version = vp.new_format_version
                                          AND new_tbl.format = vp.new_format
                                 JOIN mig_hierarchy_materialized old_tbl
                                      ON old_tbl.edifact_format_version = vp.old_format_version
                                          AND old_tbl.format = vp.old_format
                                          AND old_tbl.path = new_tbl.path)

-- Modified and unchanged rows
SELECT CASE WHEN changed_columns != '' THEN 'modified' ELSE 'unchanged' END AS diff_status,
       NULLIF(changed_columns, '')                                          AS changed_columns,
       id_path,
       sort_path,
       path,
       line_type,
       old_format_version,
       old_format,
       old_segmentgroup_id,
       old_segment_id,
       old_dataelement_id,
       old_code_value,
       old_line_status_std,
       old_line_status_specification,
       old_line_name,
       new_format_version,
       new_format,
       new_segmentgroup_id,
       new_segment_id,
       new_dataelement_id,
       new_code_value,
       new_line_status_std,
       new_line_status_specification,
       new_line_name
FROM modified_check

UNION ALL

-- Added rows (exist in new but not in old for the specific version pair)
SELECT 'added'                           AS diff_status,
       NULL                              AS changed_columns,
       new_tbl.id_path,
       new_tbl.sort_path,
       new_tbl.path,
       new_tbl.type                      AS line_type,
       vp.old_format_version             AS old_format_version,
       vp.old_format                     AS old_format,
       NULL                              AS old_segmentgroup_id,
       NULL                              AS old_segment_id,
       NULL                              AS old_dataelement_id,
       NULL                              AS old_code_value,
       NULL                              AS old_line_status_std,
       NULL                              AS old_line_status_specification,
       NULL                              AS old_line_name,
       new_tbl.edifact_format_version    AS new_format_version,
       new_tbl.format                    AS new_format,
       new_tbl.segmentgroup_id           AS new_segmentgroup_id,
       new_tbl.segment_id                AS new_segment_id,
       new_tbl.dataelement_id            AS new_dataelement_id,
       new_tbl.code_value                AS new_code_value,
       new_tbl.line_status_std           AS new_line_status_std,
       new_tbl.line_status_specification AS new_line_status_specification,
       new_tbl.line_name                 AS new_line_name
FROM version_pairs vp
         JOIN mig_hierarchy_materialized new_tbl
              ON new_tbl.edifact_format_version = vp.new_format_version
                  AND new_tbl.format = vp.new_format
WHERE NOT EXISTS (SELECT 1
                  FROM mig_hierarchy_materialized old_tbl
                  WHERE old_tbl.edifact_format_version = vp.old_format_version
                    AND old_tbl.format = vp.old_format
                    AND old_tbl.path = new_tbl.path)

UNION ALL

-- Deleted rows (exist in old but not in new for the specific version pair)
SELECT 'deleted'                         AS diff_status,
       NULL                              AS changed_columns,
       old_tbl.id_path,
       old_tbl.sort_path,
       old_tbl.path,
       old_tbl.type                      AS line_type,
       old_tbl.edifact_format_version    AS old_format_version,
       old_tbl.format                    AS old_format,
       old_tbl.segmentgroup_id           AS old_segmentgroup_id,
       old_tbl.segment_id                AS old_segment_id,
       old_tbl.dataelement_id            AS old_dataelement_id,
       old_tbl.code_value                AS old_code_value,
       old_tbl.line_status_std           AS old_line_status_std,
       old_tbl.line_status_specification AS old_line_status_specification,
       old_tbl.line_name                 AS old_line_name,
       vp.new_format_version             AS new_format_version,
       vp.new_format                     AS new_format,
       NULL                              AS new_segmentgroup_id,
       NULL                              AS new_segment_id,
       NULL                              AS new_dataelement_id,
       NULL                              AS new_code_value,
       NULL                              AS new_line_status_std,
       NULL                              AS new_line_status_specification,
       NULL                              AS new_line_name
FROM version_pairs vp
         JOIN mig_hierarchy_materialized old_tbl
              ON old_tbl.edifact_format_version = vp.old_format_version
                  AND old_tbl.format = vp.old_format
WHERE NOT EXISTS (SELECT 1
                  FROM mig_hierarchy_materialized new_tbl
                  WHERE new_tbl.edifact_format_version = vp.new_format_version
                    AND new_tbl.format = vp.new_format
                    AND new_tbl.path = old_tbl.path);
