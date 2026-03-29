-- This SQLite script materializes the hierarchy of the AHB (Anwendungshandbuch) into a table.
-- This allows for easy querying without 'unrolling' the recursive segment (group) hierarchy each time.
-- There is a Pydantic model class for the 'ahb_hierarchy_materialized' table: AhbHierarchyMaterialized

-- Drop previous materialized table if it exists
DROP TABLE IF EXISTS ahb_hierarchy_materialized;

-- ============================================================================
-- Pre-compute semantic qualifiers for segments, segment groups, and data elements.
-- These are used to build stable, version-independent id_paths.
-- A "qualifier" is the first code value in an element's subtree, e.g. '92' for DTM+92.
-- ============================================================================

-- Segment qualifier: first code value reachable from segment → DE → code (or segment → DEG → DE → code)
DROP TABLE IF EXISTS _seg_qual;
-- We prefer DEG-based codes (from EDIFACT composites like C_C082, C_C507) over direct DE codes (like D_3035)
-- because DEG structure comes from the MIG (stable across AHB versions), whereas direct DE codes
-- are AHB customizations that may be added/removed between format versions.
-- Example: NAD's D_3035 qualifier was absent in FV2510 but added in FV2604, which would change
-- the qualifier from 9 (C_C082>D_3055) to MS (D_3035). Using DEG-first keeps it stable as 9.
CREATE TEMP TABLE _seg_qual AS
SELECT s.primary_key AS pk,
       COALESCE(
           (SELECT c.value FROM dataelementgroup deg
            JOIN dataelement de ON de.data_element_group_primary_key = deg.primary_key
            JOIN code c ON c.data_element_primary_key = de.primary_key
            WHERE deg.segment_primary_key = s.primary_key
            ORDER BY deg.position, de.position, c.position LIMIT 1),
           (SELECT c.value FROM dataelement de JOIN code c ON c.data_element_primary_key = de.primary_key
            WHERE de.segment_primary_key = s.primary_key AND de.data_element_group_primary_key IS NULL
            ORDER BY de.position, c.position LIMIT 1)
       ) AS qualifier
FROM segment s;
CREATE INDEX _idx_seg_qual ON _seg_qual(pk);

-- Segments that need qualification: those with a sibling (under same parent) sharing the same id
DROP TABLE IF EXISTS _seg_needs_qual;
CREATE TEMP TABLE _seg_needs_qual AS
SELECT s1.primary_key AS pk FROM segment s1
WHERE s1.segmentgroup_primary_key IS NOT NULL
  AND EXISTS (SELECT 1 FROM segment s2
              WHERE s2.segmentgroup_primary_key = s1.segmentgroup_primary_key
                AND s2.id = s1.id AND s2.primary_key != s1.primary_key)
UNION ALL
SELECT s1.primary_key FROM segment s1
WHERE s1.segmentgroup_primary_key IS NULL
  AND EXISTS (SELECT 1 FROM segment s2
              WHERE s2.segmentgroup_primary_key IS NULL
                AND s2.anwendungsfall_primary_key = s1.anwendungsfall_primary_key
                AND s2.id = s1.id AND s2.primary_key != s1.primary_key);
CREATE INDEX _idx_seg_needs_qual ON _seg_needs_qual(pk);

-- Segment group qualifier: first code value in the SG's subtree (recursing through child SGs if needed)
DROP TABLE IF EXISTS _sg_qual;
CREATE TEMP TABLE _sg_qual AS
WITH RECURSIVE sg_qual_cte AS (
    -- Base: SGs that directly contain segments → use first segment's qualifier
    SELECT s.segmentgroup_primary_key AS sg_pk,
           (SELECT sq.qualifier FROM _seg_qual sq
            JOIN segment s2 ON sq.pk = s2.primary_key
            WHERE s2.segmentgroup_primary_key = s.segmentgroup_primary_key
            ORDER BY s2.position LIMIT 1) AS qualifier
    FROM segment s
    WHERE s.segmentgroup_primary_key IS NOT NULL
    GROUP BY s.segmentgroup_primary_key
    UNION
    -- Recursive: SGs without direct segments get qualifier from first child SG
    SELECT link.parent_id AS sg_pk, child_q.qualifier
    FROM segmentgrouplink link
    JOIN sg_qual_cte child_q ON child_q.sg_pk = link.child_id
    WHERE NOT EXISTS (SELECT 1 FROM segment s WHERE s.segmentgroup_primary_key = link.parent_id)
)
SELECT sg_pk AS pk, MIN(qualifier) AS qualifier FROM sg_qual_cte GROUP BY sg_pk HAVING qualifier IS NOT NULL;
CREATE INDEX _idx_sg_qual ON _sg_qual(pk);

-- Segment groups that need qualification: those with a sibling (under same parent) sharing the same id
DROP TABLE IF EXISTS _sg_needs_qual;
CREATE TEMP TABLE _sg_needs_qual AS
-- Child SGs under same parent SG
SELECT child1.primary_key AS pk
FROM segmentgrouplink link1
JOIN segmentgroup child1 ON link1.child_id = child1.primary_key
WHERE EXISTS (SELECT 1 FROM segmentgrouplink link2
              JOIN segmentgroup child2 ON link2.child_id = child2.primary_key
              WHERE link2.parent_id = link1.parent_id
                AND child2.id = child1.id AND child2.primary_key != child1.primary_key)
UNION ALL
-- Root-level SGs (no parent link) with same id under same anwendungsfall
SELECT sg1.primary_key FROM segmentgroup sg1
WHERE NOT EXISTS (SELECT 1 FROM segmentgrouplink link WHERE link.child_id = sg1.primary_key)
  AND EXISTS (SELECT 1 FROM segmentgroup sg2
              WHERE sg2.anwendungsfall_primary_key = sg1.anwendungsfall_primary_key
                AND sg2.id = sg1.id AND sg2.primary_key != sg1.primary_key
                AND NOT EXISTS (SELECT 1 FROM segmentgrouplink link WHERE link.child_id = sg2.primary_key));
CREATE INDEX _idx_sg_needs_qual ON _sg_needs_qual(pk);

-- Data element qualifier: first code value under the data element
DROP TABLE IF EXISTS _de_qual;
CREATE TEMP TABLE _de_qual AS
SELECT de.primary_key AS pk,
       (SELECT c.value FROM code c WHERE c.data_element_primary_key = de.primary_key
        ORDER BY c.position LIMIT 1) AS qualifier
FROM dataelement de;
CREATE INDEX _idx_de_qual ON _de_qual(pk);

-- Data elements that need qualification: those with a sibling (under same DEG) sharing the same id
DROP TABLE IF EXISTS _de_needs_qual;
CREATE TEMP TABLE _de_needs_qual AS
SELECT de1.primary_key AS pk FROM dataelement de1
WHERE de1.data_element_group_primary_key IS NOT NULL
  AND EXISTS (SELECT 1 FROM dataelement de2
              WHERE de2.data_element_group_primary_key = de1.data_element_group_primary_key
                AND de2.id = de1.id AND de2.primary_key != de1.primary_key);
CREATE INDEX _idx_de_needs_qual ON _de_needs_qual(pk);

-- ============================================================================
-- Materialize hierarchy for ALL anwendungsfaelle
-- ============================================================================

CREATE TABLE ahb_hierarchy_materialized AS -- we use a table and not a view because views may come with performance issues e.g. when joining them
WITH RECURSIVE

    ordered_roots AS (SELECT sg.primary_key,
                             sg.position,
                             'segment_group' AS type,
                             sg.id           AS root_id_text,
                             sg.name,
                             sg.ahb_status,
                             sg.anwendungsfall_primary_key,
                             NULL            AS number,
                             af.pruefidentifikator,
                             af.format,
                             ah.versionsnummer,
                             ah.gueltig_von,
                             ah.gueltig_bis,
                             af.beschreibung,
                             af.kommunikationsrichtungen,
                             ah.edifact_format_version,
                             af.anwendungshandbuch_primary_key,
                             null            as is_on_uebertragungsdatei_level
                      FROM segmentgroup sg
                               JOIN anwendungsfall af ON sg.anwendungsfall_primary_key = af.primary_key
                               JOIN anwendungshandbuch ah ON af.anwendungshandbuch_primary_key = ah.primary_key

                      UNION ALL

                      SELECT s.primary_key,
                             s.position,
                             'segment'                        AS type,
                             s.id                             AS root_id_text,
                             s.name,
                             s.ahb_status,
                             s.anwendungsfall_primary_key,
                             s.number,
                             af.pruefidentifikator,
                             af.format,
                             ah.versionsnummer,
                             ah.gueltig_von,
                             ah.gueltig_bis,
                             af.beschreibung,
                             af.kommunikationsrichtungen,
                             ah.edifact_format_version,
                             af.anwendungshandbuch_primary_key,
                             s.is_on_uebertragungsdatei_level as is_on_uebertragungsdatei_level
                      FROM segment s
                               JOIN anwendungsfall af ON s.anwendungsfall_primary_key = af.primary_key
                               JOIN anwendungshandbuch ah ON af.anwendungshandbuch_primary_key = ah.primary_key
                      WHERE s.segmentgroup_primary_key IS NULL),

    ordered_roots_with_order AS (SELECT *,
                                        ROW_NUMBER() OVER (
                                            PARTITION BY anwendungsfall_primary_key
                                            ORDER BY position
                                            ) AS root_order
                                 FROM ordered_roots),

    root_hierarchy AS (SELECT o.anwendungsfall_primary_key                                         AS anwendungsfall_pk,
                              o.primary_key                                                        AS current_id,
                              o.primary_key                                                        AS root_id,
                              NULL                                                                 AS parent_id,
                              0                                                                    AS depth,
                              o.position,
                              o.name                                                               AS path,
                              o.name                                                               AS parent_path,
                              o.root_order,
                              o.type,
                              o.primary_key                                                        AS source_id,
                              substr('00000' || o.position, -5) || '-'                             AS sort_path,
                              o.root_id_text || CASE
                                  WHEN o.type = 'segment_group'
                                       AND EXISTS (SELECT 1 FROM _sg_needs_qual sgnq WHERE sgnq.pk = o.primary_key)
                                      THEN COALESCE('+' || (SELECT sgq.qualifier FROM _sg_qual sgq WHERE sgq.pk = o.primary_key), '')
                                  WHEN o.type = 'segment'
                                       AND EXISTS (SELECT 1 FROM _seg_needs_qual snq WHERE snq.pk = o.primary_key)
                                      THEN COALESCE('+' || (SELECT sq.qualifier FROM _seg_qual sq WHERE sq.pk = o.primary_key), '')
                                  ELSE ''
                              END || '>'                                                           AS id_path,
                              o.pruefidentifikator,
                              o.format,
                              o.versionsnummer,
                              o.gueltig_von,
                              o.gueltig_bis,
                              o.beschreibung,
                              o.kommunikationsrichtungen,
                              o.edifact_format_version,
                              o.anwendungshandbuch_primary_key,
                              o.is_on_uebertragungsdatei_level,
                              CASE WHEN o.type = 'segment_group' THEN o.root_id_text ELSE NULL END AS segmentgroup_id,
                              CASE WHEN o.type = 'segment_group' THEN o.name ELSE NULL END         AS segmentgroup_name,
                              CASE WHEN o.type = 'segment_group' THEN o.ahb_status ELSE NULL END   AS segmentgroup_ahb_status,
                              CASE WHEN o.type = 'segment_group' THEN o.position ELSE NULL END     AS segmentgroup_position,
                              CASE
                                  WHEN o.type = 'segment_group' THEN o.anwendungsfall_primary_key
                                  ELSE NULL END                                                    AS segmentgroup_anwendungsfall_primary_key,

                              CASE WHEN o.type = 'segment' THEN o.root_id_text ELSE NULL END       AS segment_id,
                              CASE WHEN o.type = 'segment' THEN o.name ELSE NULL END               AS segment_name,
                              CASE WHEN o.type = 'segment' THEN o.number ELSE NULL END             AS segment_number,
                              CASE WHEN o.type = 'segment' THEN o.ahb_status ELSE NULL END         AS segment_ahb_status,
                              CASE WHEN o.type = 'segment' THEN o.position ELSE NULL END           AS segment_position,

                              NULL                                                                 AS dataelementgroup_id,
                              NULL                                                                 AS dataelementgroup_name,
                              NULL                                                                 AS dataelementgroup_position,

                              NULL                                                                 AS dataelement_id,
                              NULL                                                                 AS dataelement_name,
                              NULL                                                                 AS dataelement_position,
                              NULL                                                                 AS dataelement_ahb_status,

                              NULL                                                                 AS code_id,
                              NULL                                                                 AS code_name,
                              NULL                                                                 AS code_description,
                              NULL                                                                 AS code_value,
                              NULL                                                                 AS code_ahb_status,
                              NULL                                                                 AS code_position
                       FROM ordered_roots_with_order o),

    hierarchy AS (SELECT *
                  FROM root_hierarchy

                  UNION ALL

                  SELECT h.anwendungsfall_pk,
                         child.primary_key,
                         h.root_id,
                         link.parent_id,
                         h.depth + 1,
                         child.position,
                         h.path || ' > ' || child.name,
                         h.path,
                         h.root_order,
                         'segment_group',
                         h.source_id,
                         h.sort_path || substr('00000' || child.position, -5) || '-',
                         h.id_path || child.id || CASE
                             WHEN EXISTS (SELECT 1 FROM _sg_needs_qual sgnq WHERE sgnq.pk = child.primary_key)
                                 THEN COALESCE('+' || (SELECT sgq.qualifier FROM _sg_qual sgq WHERE sgq.pk = child.primary_key), '')
                             ELSE ''
                         END || '>',
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikationsrichtungen,
                         h.edifact_format_version,
                         h.anwendungshandbuch_primary_key,
                         h.is_on_uebertragungsdatei_level,

                         child.id,
                         child.name,
                         child.ahb_status,
                         child.position,
                         child.anwendungsfall_primary_key,

                         h.segment_id,
                         h.segment_name,
                         h.segment_number,
                         h.segment_ahb_status,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_position,
                         h.dataelement_ahb_status,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_ahb_status,
                         h.code_position
                  FROM hierarchy h
                           JOIN segmentgrouplink link ON h.current_id = link.parent_id
                           JOIN segmentgroup child ON link.child_id = child.primary_key
                  WHERE h.type = 'segment_group'

                  UNION ALL

                  SELECT h.anwendungsfall_pk,
                         s.primary_key,
                         h.root_id,
                         s.segmentgroup_primary_key,
                         h.depth + 1,
                         s.position,
                         h.path || ' > ' || s.name,
                         h.path,
                         h.root_order,
                         'segment',
                         h.source_id,
                         h.sort_path || substr('00000' || s.position, -5) || '-',
                         h.id_path || s.id || CASE
                             WHEN EXISTS (SELECT 1 FROM _seg_needs_qual snq WHERE snq.pk = s.primary_key)
                                 THEN COALESCE('+' || (SELECT sq.qualifier FROM _seg_qual sq WHERE sq.pk = s.primary_key), '')
                             ELSE ''
                         END || '>',
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikationsrichtungen,
                         h.edifact_format_version,
                         h.anwendungshandbuch_primary_key,
                         s.is_on_uebertragungsdatei_level,
                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_ahb_status,
                         h.segmentgroup_position,
                         h.segmentgroup_anwendungsfall_primary_key,

                         s.id,
                         s.name,
                         s.number,
                         s.ahb_status,
                         s.position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_position,
                         h.dataelement_ahb_status,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_ahb_status,
                         h.code_position
                  FROM hierarchy h
                           JOIN segment s ON s.segmentgroup_primary_key = h.current_id
                  WHERE h.type = 'segment_group'

                  UNION ALL

                  SELECT h.anwendungsfall_pk,
                         deg.primary_key,
                         h.root_id,
                         deg.segment_primary_key,
                         h.depth + 1,
                         deg.position,
                         h.path || ' > ' || deg.name,
                         h.path,
                         h.root_order,
                         'dataelementgroup',
                         h.source_id,
                         h.sort_path || substr('00000' || deg.position, -5) || '-',
                         h.id_path || deg.id || '>',
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikationsrichtungen,
                         h.edifact_format_version,
                         h.anwendungshandbuch_primary_key,
                         h.is_on_uebertragungsdatei_level,
                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_ahb_status,
                         h.segmentgroup_position,
                         h.segmentgroup_anwendungsfall_primary_key,

                         h.segment_id,
                         h.segment_name,
                         h.segment_number,
                         h.segment_ahb_status,
                         h.segment_position,

                         deg.id,
                         deg.name,
                         deg.position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_position,
                         h.dataelement_ahb_status,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_ahb_status,
                         h.code_position
                  FROM hierarchy h
                           JOIN dataelementgroup deg ON deg.segment_primary_key = h.current_id
                  WHERE h.type = 'segment'

                  UNION ALL

                  SELECT h.anwendungsfall_pk,
                         de.primary_key,
                         h.root_id,
                         de.segment_primary_key,
                         h.depth + 1,
                         de.position,
                         h.path || ' > ' || de.name,
                         h.path,
                         h.root_order,
                         'dataelement',
                         h.source_id,
                         h.sort_path || substr('00000' || de.position, -5) || '-',
                         h.id_path || de.id || '>',
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikationsrichtungen,
                         h.edifact_format_version,
                         h.anwendungshandbuch_primary_key,
                         h.is_on_uebertragungsdatei_level,
                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_ahb_status,
                         h.segmentgroup_position,
                         h.segmentgroup_anwendungsfall_primary_key,

                         h.segment_id,
                         h.segment_name,
                         h.segment_number,
                         h.segment_ahb_status,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_position,

                         de.id,
                         de.name,
                         de.position,
                         de.ahb_status,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_ahb_status,
                         h.code_position
                  FROM hierarchy h
                           JOIN dataelement de ON de.segment_primary_key = h.current_id
                  WHERE h.type = 'segment'
                    AND de.data_element_group_primary_key IS NULL

                  UNION ALL

                  SELECT h.anwendungsfall_pk,
                         de.primary_key,
                         h.root_id,
                         de.data_element_group_primary_key,
                         h.depth + 1,
                         de.position,
                         h.path || ' > ' || de.name,
                         h.path,
                         h.root_order,
                         'dataelement',
                         h.source_id,
                         h.sort_path || substr('00000' || de.position, -5) || '-',
                         h.id_path || de.id || CASE
                             WHEN EXISTS (SELECT 1 FROM _de_needs_qual dnq WHERE dnq.pk = de.primary_key)
                                 THEN COALESCE('+' || (SELECT dq.qualifier FROM _de_qual dq WHERE dq.pk = de.primary_key), '')
                             ELSE ''
                         END || '>',
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikationsrichtungen,
                         h.edifact_format_version,
                         h.anwendungshandbuch_primary_key,
                         h.is_on_uebertragungsdatei_level,
                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_ahb_status,
                         h.segmentgroup_position,
                         h.segmentgroup_anwendungsfall_primary_key,

                         h.segment_id,
                         h.segment_name,
                         h.segment_number,
                         h.segment_ahb_status,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_position,

                         de.id,
                         de.name,
                         de.position,
                         de.ahb_status,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_ahb_status,
                         h.code_position
                  FROM hierarchy h
                           JOIN dataelement de ON de.data_element_group_primary_key = h.current_id
                  WHERE h.type = 'dataelementgroup'

                  UNION ALL

                  SELECT h.anwendungsfall_pk,
                         c.primary_key,
                         h.root_id,
                         c.data_element_primary_key,
                         h.depth + 1,
                         c.position,
                         h.path || ' > ' || c.name,
                         h.path,
                         h.root_order,
                         'code',
                         h.source_id,
                         h.sort_path || substr('00000' || c.position, -5) || '-',
                         h.id_path || c.value || '>',
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikationsrichtungen,
                         h.edifact_format_version,
                         h.anwendungshandbuch_primary_key,
                         h.is_on_uebertragungsdatei_level,
                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_ahb_status,
                         h.segmentgroup_position,
                         h.segmentgroup_anwendungsfall_primary_key,

                         h.segment_id,
                         h.segment_name,
                         h.segment_number,
                         h.segment_ahb_status,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_position,
                         h.dataelement_ahb_status,

                         c.primary_key,
                         c.name,
                         c.description,
                         c.value,
                         c.ahb_status,
                         c.position
                  FROM hierarchy h
                           JOIN code c ON c.data_element_primary_key = h.current_id
                  WHERE h.type = 'dataelement')

SELECT hex(randomblob(16)) AS id,
       *,
       -- add 2 computed columns which are used in v_ahbtabellen only but not indexable if they were not real columns (but just an expression inside a view definition)
       trim(
               coalesce(
                       code_name,
                       dataelement_name,
                       dataelementgroup_name,
                       segment_name,
                       segmentgroup_name
               )
       )                   as line_name,
       trim(
               coalesce(
                       code_ahb_status,
                       dataelement_ahb_status,
                       segment_ahb_status,
                       segmentgroup_ahb_status
               )
       )                   as line_ahb_status
FROM hierarchy
ORDER BY anwendungsfall_pk, sort_path;



CREATE UNIQUE INDEX idx_hierarchy_id ON ahb_hierarchy_materialized (id);
CREATE INDEX idx_hierarchy_afpk ON ahb_hierarchy_materialized (anwendungsfall_pk);
CREATE INDEX idx_hierarchy_awfpk_sort ON ahb_hierarchy_materialized (anwendungsfall_pk, sort_path);
CREATE INDEX idx_hierarchy_type ON ahb_hierarchy_materialized (type);
CREATE INDEX idx_hierarchy_pruefidentifikator ON ahb_hierarchy_materialized (pruefidentifikator);
CREATE INDEX idx_hierarchy_format ON ahb_hierarchy_materialized (format);
CREATE INDEX idx_hierarchy_format_format_version ON ahb_hierarchy_materialized (format, edifact_format_version);
CREATE INDEX idx_hierarchy_versionsnummer ON ahb_hierarchy_materialized (versionsnummer);
CREATE INDEX idx_hierarchy_gueltig_von ON ahb_hierarchy_materialized (gueltig_von);
CREATE INDEX idx_hierarchy_gueltig_bis ON ahb_hierarchy_materialized (gueltig_bis);
CREATE INDEX idx_hierarchy_beschreibung ON ahb_hierarchy_materialized (beschreibung);
CREATE INDEX idx_hierarchy_beschreibung_lower ON ahb_hierarchy_materialized (lower(beschreibung));
CREATE INDEX idx_hierarchy_kommunikationsrichtungen ON ahb_hierarchy_materialized (kommunikationsrichtungen);
CREATE INDEX idx_hierarchy_edifact_format_version ON ahb_hierarchy_materialized (edifact_format_version);
CREATE INDEX idx_hierarchy_segmentgroup_id ON ahb_hierarchy_materialized (segmentgroup_id);
CREATE INDEX idx_hierarchy_segmentgroup_id_lower ON ahb_hierarchy_materialized (lower(segmentgroup_id));
CREATE INDEX idx_hierarchy_segmentgroup_name ON ahb_hierarchy_materialized (segmentgroup_name);
CREATE INDEX idx_hierarchy_segmentgroup_position ON ahb_hierarchy_materialized (segmentgroup_position);
CREATE INDEX idx_hierarchy_segment_id ON ahb_hierarchy_materialized (segment_id);
CREATE INDEX idx_hierarchy_segment_id_lower ON ahb_hierarchy_materialized (lower(segment_id));
CREATE INDEX idx_hierarchy_segment_name ON ahb_hierarchy_materialized (segment_name);
CREATE INDEX idx_hierarchy_segment_number ON ahb_hierarchy_materialized (segment_number);
CREATE INDEX idx_hierarchy_segment_position ON ahb_hierarchy_materialized (segment_position);
CREATE INDEX idx_hierarchy_dataelementgroup_id ON ahb_hierarchy_materialized (dataelementgroup_id);
CREATE INDEX idx_hierarchy_dataelementgroup_name ON ahb_hierarchy_materialized (dataelementgroup_name);
CREATE INDEX idx_hierarchy_dataelementgroup_position ON ahb_hierarchy_materialized (dataelementgroup_position);
CREATE INDEX idx_hierarchy_dataelement_id ON ahb_hierarchy_materialized (dataelement_id);
CREATE INDEX idx_hierarchy_dataelement_id_lower ON ahb_hierarchy_materialized (lower(dataelement_id));
CREATE INDEX idx_hierarchy_dataelement_name ON ahb_hierarchy_materialized (dataelement_name);
CREATE INDEX idx_hierarchy_dataelement_position ON ahb_hierarchy_materialized (dataelement_position);
CREATE INDEX idx_hierarchy_dataelement_ahb_status ON ahb_hierarchy_materialized (dataelement_ahb_status);
CREATE INDEX idx_hierarchy_code_id ON ahb_hierarchy_materialized (code_id);
CREATE INDEX idx_hierarchy_code_name ON ahb_hierarchy_materialized (code_name);
CREATE INDEX idx_hierarchy_code_description ON ahb_hierarchy_materialized (code_description);
CREATE INDEX idx_hierarchy_code_description_lower ON ahb_hierarchy_materialized (lower(code_description));
CREATE INDEX idx_hierarchy_code_value ON ahb_hierarchy_materialized (code_value);
CREATE INDEX idx_hierarchy_code_value_lower ON ahb_hierarchy_materialized (lower(code_value));
CREATE INDEX idx_hierarchy_code_ahb_status ON ahb_hierarchy_materialized (code_ahb_status);
CREATE INDEX idx_hierarchy_code_position ON ahb_hierarchy_materialized (code_position);
CREATE INDEX idx_hierarchy_path ON ahb_hierarchy_materialized (path);
CREATE INDEX idx_hierarchy_id_path ON ahb_hierarchy_materialized (id_path);
CREATE INDEX idx_hierarchy_sort ON ahb_hierarchy_materialized (sort_path);

-- the following 2 indexes are to speed of v_ahbtabellen only
CREATE INDEX idx_ahb_tabellen_filter1 ON ahb_hierarchy_materialized (dataelement_ahb_status) WHERE type = 'dataelement' AND dataelement_ahb_status IS NOT NULL;
CREATE INDEX idx_ahb_tabellen_filter2 ON ahb_hierarchy_materialized (type) WHERE type <> 'dataelementgroup';

-- indexes for computed columns for v_ahbtabellen
CREATE INDEX idx_line_ahb_status ON ahb_hierarchy_materialized (line_ahb_status);
CREATE INDEX idx_line_ahb_status_lower ON ahb_hierarchy_materialized (lower(line_ahb_status));
CREATE INDEX idx_line_name ON ahb_hierarchy_materialized (line_name);
CREATE INDEX idx_line_name_lower ON ahb_hierarchy_materialized (lower(line_name));
CREATE INDEX idx_hierarchy_sort_path_per_ahb ON ahb_hierarchy_materialized (sort_path, pruefidentifikator, edifact_format_version);

-- Fallback: append occurrence counter '#N' to any id_paths that are still not unique after qualifier injection.
-- This handles edge cases where the qualifier is NULL (no code children) or shared among siblings:
-- - IFTSTA (prüfi 21045): flat segment group naming leads to multiple STS segments with the same
--   qualifier under identical structural paths. See #258 by hf-mrdachner for details.
-- - PARTIN FII: repeated "Name des Kontoinhabers" (D_3192) fields, see #259
-- - PRICAT IMD: repeated IMD segments under the same path
-- The counter is local (counts only within the duplicate group), so it's stable as long as the
-- number and order of identical siblings doesn't change between versions.
-- NOTE: We pre-compute counter values in a temp table because SQLite's UPDATE processes rows sequentially,
-- which means subqueries in the SET clause see already-modified rows, breaking self-referencing counters.
CREATE TEMP TABLE _id_path_counter_fix AS
SELECT id,
       id_path || '#' || ROW_NUMBER() OVER (
           PARTITION BY id_path, pruefidentifikator, edifact_format_version
           ORDER BY sort_path, id
       ) AS new_id_path
FROM ahb_hierarchy_materialized
WHERE id IN (SELECT h1.id
             FROM ahb_hierarchy_materialized h1
             WHERE EXISTS (SELECT 1
                           FROM ahb_hierarchy_materialized h2
                           WHERE h2.id_path = h1.id_path
                             AND h2.pruefidentifikator = h1.pruefidentifikator
                             AND (h2.edifact_format_version = h1.edifact_format_version OR
                                  (h2.edifact_format_version IS NULL AND h1.edifact_format_version IS NULL))
                             AND h2.id != h1.id));

CREATE UNIQUE INDEX _idx_counter_fix ON _id_path_counter_fix(id);

UPDATE ahb_hierarchy_materialized
SET id_path = (SELECT cf.new_id_path FROM _id_path_counter_fix cf WHERE cf.id = ahb_hierarchy_materialized.id)
WHERE id IN (SELECT id FROM _id_path_counter_fix);

DROP TABLE _id_path_counter_fix;

-- Clean up temporary qualifier tables
DROP TABLE IF EXISTS _seg_qual;
DROP TABLE IF EXISTS _seg_needs_qual;
DROP TABLE IF EXISTS _sg_qual;
DROP TABLE IF EXISTS _sg_needs_qual;
DROP TABLE IF EXISTS _de_qual;
DROP TABLE IF EXISTS _de_needs_qual;

-- if the unique part of the following indexes raises an integrity error, this is handled by the calling python code
-- column order optimized for v_ahb_diff queries: filter by (version, pruefi) first, then lookup by id_path/path
CREATE UNIQUE INDEX idx_hierarchy_id_path_per_ahb ON ahb_hierarchy_materialized (edifact_format_version, pruefidentifikator, id_path);

CREATE UNIQUE INDEX idx_hierarchy_path_per_ahb ON ahb_hierarchy_materialized (edifact_format_version, pruefidentifikator, path);

