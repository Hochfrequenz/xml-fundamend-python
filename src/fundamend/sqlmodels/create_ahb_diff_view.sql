-- Assume that materialize_ahb_view.sql and create_ahbtabellen_view.sql have been executed already.
-- This view allows comparing two AHB versions (using v_ahbtabellen) to find added, deleted, and modified rows.
--
-- IMPORTANT: This view produces a cross-product of all version pairs. You MUST filter by version and pruefidentifikator.
--
-- Usage for comparing FV2410 -> FV2504 for pruefidentifikator 55014:
--   SELECT * FROM v_ahb_diff
--   WHERE old_format_version = 'FV2410'
--     AND old_pruefidentifikator = '55014'
--     AND new_format_version = 'FV2504'
--     AND new_pruefidentifikator = '55014'
--   ORDER BY sort_path;
--
-- diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
-- The view compares line_ahb_status, bedingung, and line_name to determine modifications.
--
-- For deleted rows, old_ columns are populated and new_ columns are NULL.
-- For added rows, new_ columns are populated and old_ columns are NULL.

DROP TABLE IF EXISTS v_ahb_diff;
DROP VIEW IF EXISTS v_ahb_diff;

CREATE VIEW v_ahb_diff AS
-- All comparison pairs: new x old (full join simulated via LEFT JOINs + UNION)
-- This includes: added (new only), deleted (old only), modified, unchanged
SELECT
    CASE
        WHEN old_tbl.id_path IS NULL THEN 'added'
        WHEN COALESCE(old_tbl.line_ahb_status, '') != COALESCE(new_tbl.line_ahb_status, '')
          OR COALESCE(old_tbl.bedingung, '') != COALESCE(new_tbl.bedingung, '')
          OR COALESCE(old_tbl.line_name, '') != COALESCE(new_tbl.line_name, '')
        THEN 'modified'
        ELSE 'unchanged'
    END AS diff_status,
    COALESCE(new_tbl.id_path, old_tbl.id_path) AS id_path,
    COALESCE(new_tbl.sort_path, old_tbl.sort_path) AS sort_path,
    COALESCE(new_tbl.path, old_tbl.path) AS path,
    COALESCE(new_tbl.line_type, old_tbl.line_type) AS line_type,
    -- Old version columns
    old_tbl.format_version AS old_format_version,
    old_tbl.pruefidentifikator AS old_pruefidentifikator,
    old_tbl.segmentgroup_key AS old_segmentgroup_key,
    old_tbl.segment_code AS old_segment_code,
    old_tbl.data_element AS old_data_element,
    old_tbl.qualifier AS old_qualifier,
    old_tbl.line_ahb_status AS old_line_ahb_status,
    old_tbl.line_name AS old_line_name,
    old_tbl.bedingung AS old_bedingung,
    old_tbl.bedingungsfehler AS old_bedingungsfehler,
    -- New version columns
    new_tbl.format_version AS new_format_version,
    new_tbl.pruefidentifikator AS new_pruefidentifikator,
    new_tbl.segmentgroup_key AS new_segmentgroup_key,
    new_tbl.segment_code AS new_segment_code,
    new_tbl.data_element AS new_data_element,
    new_tbl.qualifier AS new_qualifier,
    new_tbl.line_ahb_status AS new_line_ahb_status,
    new_tbl.line_name AS new_line_name,
    new_tbl.bedingung AS new_bedingung,
    new_tbl.bedingungsfehler AS new_bedingungsfehler
FROM v_ahbtabellen new_tbl
LEFT JOIN v_ahbtabellen old_tbl ON new_tbl.id_path = old_tbl.id_path

UNION ALL

-- Deleted rows (in old but not in new) - only rows where id_path doesn't match ANY new row
SELECT
    'deleted' AS diff_status,
    old_tbl.id_path,
    old_tbl.sort_path,
    old_tbl.path,
    old_tbl.line_type,
    -- Old version columns
    old_tbl.format_version AS old_format_version,
    old_tbl.pruefidentifikator AS old_pruefidentifikator,
    old_tbl.segmentgroup_key AS old_segmentgroup_key,
    old_tbl.segment_code AS old_segment_code,
    old_tbl.data_element AS old_data_element,
    old_tbl.qualifier AS old_qualifier,
    old_tbl.line_ahb_status AS old_line_ahb_status,
    old_tbl.line_name AS old_line_name,
    old_tbl.bedingung AS old_bedingung,
    old_tbl.bedingungsfehler AS old_bedingungsfehler,
    -- New version columns populated from the attempted join target for filtering
    new_tbl.format_version AS new_format_version,
    new_tbl.pruefidentifikator AS new_pruefidentifikator,
    NULL AS new_segmentgroup_key,
    NULL AS new_segment_code,
    NULL AS new_data_element,
    NULL AS new_qualifier,
    NULL AS new_line_ahb_status,
    NULL AS new_line_name,
    NULL AS new_bedingung,
    NULL AS new_bedingungsfehler
FROM v_ahbtabellen old_tbl
CROSS JOIN (SELECT DISTINCT format_version, pruefidentifikator FROM v_ahbtabellen) new_tbl
WHERE NOT EXISTS (
    SELECT 1 FROM v_ahbtabellen existing_new
    WHERE existing_new.id_path = old_tbl.id_path
      AND existing_new.format_version = new_tbl.format_version
      AND existing_new.pruefidentifikator = new_tbl.pruefidentifikator
);
