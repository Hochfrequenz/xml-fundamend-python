-- Assume that materialize_ahb_view.sql and create_ahbtabellen_view.sql have been executed already.
-- This view allows comparing two DIFFERENT Pruefidentifikatoren within the SAME AHB format version
-- (using v_ahbtabellen) to find added, deleted, and modified rows.
-- For comparing the SAME Pruefidentifikator across two format versions, see v_ahb_formatversion_diff
-- (create_ahb_formatversion_diff_view.sql) instead.
--
-- IMPORTANT: This view produces a cross-product of all pruefidentifikator pairs per format version.
-- You MUST filter by format version and both pruefidentifikatoren.
--
-- Usage for comparing pruefidentifikator 55014 -> 55024 within FV2504:
--   SELECT * FROM v_ahb_pruefi_diff
--   WHERE old_format_version = 'FV2504'
--     AND new_format_version = 'FV2504'
--     AND old_pruefidentifikator = '55014'
--     AND new_pruefidentifikator = '55024'
--   ORDER BY sort_path;
-- ⚠️ there's a limitation to use old pruefidentifikator < new pruefidentifikator within the same format version
--
-- diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
-- The view compares line_ahb_status, bedingung, and line_name to determine modifications.
--
-- For deleted rows, old_ columns are populated and new_ columns are NULL.
-- For added rows, new_ columns are populated and old_ columns are NULL.

DROP TABLE IF EXISTS v_ahb_pruefi_diff;
DROP VIEW IF EXISTS v_ahb_pruefi_diff;

CREATE VIEW v_ahb_pruefi_diff AS
WITH version_pairs AS (SELECT DISTINCT old_v.format_version     AS format_version,
                                       old_v.pruefidentifikator AS old_pruefidentifikator,
                                       new_v.pruefidentifikator AS new_pruefidentifikator
                       FROM (SELECT DISTINCT format_version, pruefidentifikator FROM v_ahbtabellen) old_v
                                JOIN (SELECT DISTINCT format_version, pruefidentifikator FROM v_ahbtabellen) new_v
                                     ON old_v.format_version = new_v.format_version
                       WHERE old_v.pruefidentifikator < new_v.pruefidentifikator),

-- Pre-compute changed_columns once, derive diff_status from it
-- Note: SQLite's "IS NOT" is a NULL-safe inequality operator (equivalent to SQL standard "IS DISTINCT FROM")
     modified_check AS (SELECT TRIM(
                                       CASE
                                           WHEN old_tbl.line_ahb_status IS NOT new_tbl.line_ahb_status
                                               THEN 'line_ahb_status, '
                                           ELSE '' END ||
                                       CASE
                                           WHEN old_tbl.bedingung IS NOT new_tbl.bedingung
                                               THEN 'bedingung, '
                                           ELSE '' END ||
                                       CASE
                                           WHEN old_tbl.line_name IS NOT new_tbl.line_name
                                               THEN 'line_name'
                                           ELSE '' END
                                   , ', ')                AS changed_columns,
                               new_tbl.id_path            AS id_path,
                               new_tbl.sort_path          AS sort_path,
                               new_tbl.path               AS path,
                               new_tbl.line_type          AS line_type,
                               old_tbl.format_version     AS old_format_version,
                               old_tbl.pruefidentifikator AS old_pruefidentifikator,
                               old_tbl.segmentgroup_key   AS old_segmentgroup_key,
                               old_tbl.segment_code       AS old_segment_code,
                               old_tbl.data_element       AS old_data_element,
                               old_tbl.qualifier          AS old_qualifier,
                               old_tbl.line_ahb_status    AS old_line_ahb_status,
                               old_tbl.line_name          AS old_line_name,
                               old_tbl.bedingung          AS old_bedingung,
                               old_tbl.bedingungsfehler   AS old_bedingungsfehler,
                               new_tbl.format_version     AS new_format_version,
                               new_tbl.pruefidentifikator AS new_pruefidentifikator,
                               new_tbl.segmentgroup_key   AS new_segmentgroup_key,
                               new_tbl.segment_code       AS new_segment_code,
                               new_tbl.data_element       AS new_data_element,
                               new_tbl.qualifier          AS new_qualifier,
                               new_tbl.line_ahb_status    AS new_line_ahb_status,
                               new_tbl.line_name          AS new_line_name,
                               new_tbl.bedingung          AS new_bedingung,
                               new_tbl.bedingungsfehler   AS new_bedingungsfehler
                        FROM version_pairs vp
                                 JOIN v_ahbtabellen new_tbl
                                      ON new_tbl.format_version = vp.format_version
                                          AND new_tbl.pruefidentifikator = vp.new_pruefidentifikator
                                 JOIN v_ahbtabellen old_tbl
                                      ON old_tbl.format_version = vp.format_version
                                          AND old_tbl.pruefidentifikator = vp.old_pruefidentifikator
                                          AND old_tbl.id_path = new_tbl.id_path)

-- Modified and unchanged rows
SELECT CASE WHEN changed_columns != '' THEN 'modified' ELSE 'unchanged' END AS diff_status,
       NULLIF(changed_columns, '')                                          AS changed_columns,
       id_path,
       sort_path,
       path,
       line_type,
       old_format_version,
       old_pruefidentifikator,
       old_segmentgroup_key,
       old_segment_code,
       old_data_element,
       old_qualifier,
       old_line_ahb_status,
       old_line_name,
       old_bedingung,
       old_bedingungsfehler,
       new_format_version,
       new_pruefidentifikator,
       new_segmentgroup_key,
       new_segment_code,
       new_data_element,
       new_qualifier,
       new_line_ahb_status,
       new_line_name,
       new_bedingung,
       new_bedingungsfehler
FROM modified_check

UNION ALL

-- Added rows (exist for new_pruefidentifikator but not for old_pruefidentifikator, within the format version)
SELECT 'added'                    AS diff_status,
       NULL                       AS changed_columns,
       new_tbl.id_path,
       new_tbl.sort_path,
       new_tbl.path,
       new_tbl.line_type,
       vp.format_version          AS old_format_version,
       vp.old_pruefidentifikator  AS old_pruefidentifikator,
       NULL                       AS old_segmentgroup_key,
       NULL                       AS old_segment_code,
       NULL                       AS old_data_element,
       NULL                       AS old_qualifier,
       NULL                       AS old_line_ahb_status,
       NULL                       AS old_line_name,
       NULL                       AS old_bedingung,
       NULL                       AS old_bedingungsfehler,
       new_tbl.format_version     AS new_format_version,
       new_tbl.pruefidentifikator AS new_pruefidentifikator,
       new_tbl.segmentgroup_key   AS new_segmentgroup_key,
       new_tbl.segment_code       AS new_segment_code,
       new_tbl.data_element       AS new_data_element,
       new_tbl.qualifier          AS new_qualifier,
       new_tbl.line_ahb_status    AS new_line_ahb_status,
       new_tbl.line_name          AS new_line_name,
       new_tbl.bedingung          AS new_bedingung,
       new_tbl.bedingungsfehler   AS new_bedingungsfehler
FROM version_pairs vp
         JOIN v_ahbtabellen new_tbl
              ON new_tbl.format_version = vp.format_version
                  AND new_tbl.pruefidentifikator = vp.new_pruefidentifikator
WHERE NOT EXISTS (SELECT 1
                  FROM v_ahbtabellen old_tbl
                  WHERE old_tbl.format_version = vp.format_version
                    AND old_tbl.pruefidentifikator = vp.old_pruefidentifikator
                    AND old_tbl.id_path = new_tbl.id_path)

UNION ALL

-- Deleted rows (exist for old_pruefidentifikator but not for new_pruefidentifikator, within the format version)
SELECT 'deleted'                  AS diff_status,
       NULL                       AS changed_columns,
       old_tbl.id_path,
       old_tbl.sort_path,
       old_tbl.path,
       old_tbl.line_type,
       old_tbl.format_version     AS old_format_version,
       old_tbl.pruefidentifikator AS old_pruefidentifikator,
       old_tbl.segmentgroup_key   AS old_segmentgroup_key,
       old_tbl.segment_code       AS old_segment_code,
       old_tbl.data_element       AS old_data_element,
       old_tbl.qualifier          AS old_qualifier,
       old_tbl.line_ahb_status    AS old_line_ahb_status,
       old_tbl.line_name          AS old_line_name,
       old_tbl.bedingung          AS old_bedingung,
       old_tbl.bedingungsfehler   AS old_bedingungsfehler,
       vp.format_version          AS new_format_version,
       vp.new_pruefidentifikator  AS new_pruefidentifikator,
       NULL                       AS new_segmentgroup_key,
       NULL                       AS new_segment_code,
       NULL                       AS new_data_element,
       NULL                       AS new_qualifier,
       NULL                       AS new_line_ahb_status,
       NULL                       AS new_line_name,
       NULL                       AS new_bedingung,
       NULL                       AS new_bedingungsfehler
FROM version_pairs vp
         JOIN v_ahbtabellen old_tbl
              ON old_tbl.format_version = vp.format_version
                  AND old_tbl.pruefidentifikator = vp.old_pruefidentifikator
WHERE NOT EXISTS (SELECT 1
                  FROM v_ahbtabellen new_tbl
                  WHERE new_tbl.format_version = vp.format_version
                    AND new_tbl.pruefidentifikator = vp.new_pruefidentifikator
                    AND new_tbl.id_path = old_tbl.id_path);
