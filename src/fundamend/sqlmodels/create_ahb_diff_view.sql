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
-- ⚠️ from fundamend >=v0.31 on, there's a limitation to use old prüfi = new prüfi and old FV < new FV
--
-- diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
-- The view compares line_ahb_status, bedingung, and line_name to determine modifications.
--
-- For deleted rows, old_ columns are populated and new_ columns are NULL.
-- For added rows, new_ columns are populated and old_ columns are NULL.

DROP TABLE IF EXISTS v_ahb_diff;
DROP VIEW IF EXISTS v_ahb_diff;

CREATE VIEW v_ahb_diff AS
-- Generate all version pairs first, then do proper matching within each pair
-- This approach creates the cross-product of version pairs, then finds added/deleted/modified/unchanged
WITH version_pairs AS (
    -- All possible pairs of (old_version, old_pruefi) x (new_version, new_pruefi)
    SELECT DISTINCT
        old_v.format_version AS old_format_version,
        old_v.pruefidentifikator AS old_pruefidentifikator,
        new_v.format_version AS new_format_version,
        new_v.pruefidentifikator AS new_pruefidentifikator
    FROM (SELECT DISTINCT format_version, pruefidentifikator FROM v_ahbtabellen) old_v
    CROSS JOIN (SELECT DISTINCT format_version, pruefidentifikator FROM v_ahbtabellen) new_v
-- ⚠️ from fundamend >=v0.31 on, there's a limitation to use old prüfi = new prüfi and old FV < new FV
    ON old_v.pruefidentifikator = new_v.pruefidentifikator
    WHERE old_v.format_version < new_v.format_version
)
-- Modified and unchanged rows (exist in both old and new for the same id_path within the pair)
SELECT
    CASE
        WHEN COALESCE(old_tbl.line_ahb_status, '') != COALESCE(new_tbl.line_ahb_status, '')
          OR COALESCE(old_tbl.bedingung, '') != COALESCE(new_tbl.bedingung, '')
          OR COALESCE(old_tbl.line_name, '') != COALESCE(new_tbl.line_name, '')
        THEN 'modified'
        ELSE 'unchanged'
    END AS diff_status,
    CASE
        WHEN COALESCE(old_tbl.line_ahb_status, '') != COALESCE(new_tbl.line_ahb_status, '')
          OR COALESCE(old_tbl.bedingung, '') != COALESCE(new_tbl.bedingung, '')
          OR COALESCE(old_tbl.line_name, '') != COALESCE(new_tbl.line_name, '')
        THEN
            TRIM(
                CASE WHEN COALESCE(old_tbl.line_ahb_status, '') != COALESCE(new_tbl.line_ahb_status, '')
                     THEN 'line_ahb_status, ' ELSE '' END ||
                CASE WHEN COALESCE(old_tbl.bedingung, '') != COALESCE(new_tbl.bedingung, '')
                     THEN 'bedingung, ' ELSE '' END ||
                CASE WHEN COALESCE(old_tbl.line_name, '') != COALESCE(new_tbl.line_name, '')
                     THEN 'line_name' ELSE '' END
            , ', ')
        ELSE NULL
    END AS changed_columns,
    new_tbl.id_path AS id_path,
    new_tbl.sort_path AS sort_path,
    new_tbl.path AS path,
    new_tbl.line_type AS line_type,
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
FROM version_pairs vp
JOIN v_ahbtabellen new_tbl
    ON new_tbl.format_version = vp.new_format_version
    AND new_tbl.pruefidentifikator = vp.new_pruefidentifikator
JOIN v_ahbtabellen old_tbl
    ON old_tbl.format_version = vp.old_format_version
    AND old_tbl.pruefidentifikator = vp.old_pruefidentifikator
    AND old_tbl.id_path = new_tbl.id_path

UNION ALL

-- Added rows (exist in new but not in old for the specific version pair)
SELECT
    'added' AS diff_status,
    NULL AS changed_columns,
    new_tbl.id_path,
    new_tbl.sort_path,
    new_tbl.path,
    new_tbl.line_type,
    -- Old version columns (NULL for added rows)
    vp.old_format_version AS old_format_version,
    vp.old_pruefidentifikator AS old_pruefidentifikator,
    NULL AS old_segmentgroup_key,
    NULL AS old_segment_code,
    NULL AS old_data_element,
    NULL AS old_qualifier,
    NULL AS old_line_ahb_status,
    NULL AS old_line_name,
    NULL AS old_bedingung,
    NULL AS old_bedingungsfehler,
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
FROM version_pairs vp
JOIN v_ahbtabellen new_tbl
    ON new_tbl.format_version = vp.new_format_version
    AND new_tbl.pruefidentifikator = vp.new_pruefidentifikator
WHERE NOT EXISTS (
    SELECT 1 FROM v_ahbtabellen old_tbl
    WHERE old_tbl.format_version = vp.old_format_version
      AND old_tbl.pruefidentifikator = vp.old_pruefidentifikator
      AND old_tbl.id_path = new_tbl.id_path
)

UNION ALL

-- Deleted rows (exist in old but not in new for the specific version pair)
SELECT
    'deleted' AS diff_status,
    NULL AS changed_columns,
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
    -- New version columns (NULL for deleted rows, except version/pruefi for filtering)
    vp.new_format_version AS new_format_version,
    vp.new_pruefidentifikator AS new_pruefidentifikator,
    NULL AS new_segmentgroup_key,
    NULL AS new_segment_code,
    NULL AS new_data_element,
    NULL AS new_qualifier,
    NULL AS new_line_ahb_status,
    NULL AS new_line_name,
    NULL AS new_bedingung,
    NULL AS new_bedingungsfehler
FROM version_pairs vp
JOIN v_ahbtabellen old_tbl
    ON old_tbl.format_version = vp.old_format_version
    AND old_tbl.pruefidentifikator = vp.old_pruefidentifikator
WHERE NOT EXISTS (
    SELECT 1 FROM v_ahbtabellen new_tbl
    WHERE new_tbl.format_version = vp.new_format_version
      AND new_tbl.pruefidentifikator = vp.new_pruefidentifikator
      AND new_tbl.id_path = old_tbl.id_path
);
