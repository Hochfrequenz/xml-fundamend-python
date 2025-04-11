-- This SQLite script materializes the hierarchy of the AHB (Anwendungshandbuch) into a table.
-- This allows for easy querying without 'unrolling' the recursive segment (group) hierarchy each time.
-- There is a Pydantic model class for the 'ahb_hierarchy_materialized' table: AhbHierarchyMaterialized

-- Drop previous materialized table if it exists
DROP TABLE IF EXISTS ahb_hierarchy_materialized;

-- Materialize hierarchy for ALL anwendungsfaelle
CREATE TABLE ahb_hierarchy_materialized AS -- we use a table and not a view because views may come with performance issues e.g. when joining them
WITH RECURSIVE

    ordered_roots AS (SELECT sg.primary_key,
                             sg.position,
                             'segment_group' AS type,
                             'SG' || sg.id   AS root_id_text,
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
                             af.kommunikation_von,
                             ah.edifact_format_version
                      FROM segmentgroup sg
                               JOIN anwendungsfall af ON sg.anwendungsfall_primary_key = af.primary_key
                               JOIN anwendungshandbuch ah ON af.anwendungshandbuch_primary_key = ah.primary_key

                      UNION ALL

                      SELECT s.primary_key,
                             s.position,
                             'segment' AS type,
                             s.id      AS root_id_text,
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
                             af.kommunikation_von,
                             ah.edifact_format_version

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
                              o.root_id_text || '>'                                                AS id_path,
                              o.pruefidentifikator,
                              o.format,
                              o.versionsnummer,
                              o.gueltig_von,
                              o.gueltig_bis,
                              o.beschreibung,
                              o.kommunikation_von,
                              o.edifact_format_version,

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
                         h.sort_path || substr('00000' || child.position, -5) || '-' AS sort_path,
                         h.id_path || 'SG' || child.id || '>'                        AS id_path,
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikation_von,
                         h.edifact_format_version,

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
                         h.sort_path || substr('00000' || s.position, -5) || '-' AS sort_path,
                         h.id_path || s.id || '>'                                AS id_path,
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikation_von,
                         h.edifact_format_version,

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
                         h.sort_path || substr('00000' || deg.position, -5) || '-' AS sort_path,
                         h.id_path || deg.id || '>'                                AS id_path,
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikation_von,
                         h.edifact_format_version,

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
                         h.sort_path || substr('00000' || de.position, -5) || '-' AS sort_path,
                         h.id_path || de.id || '>'                                AS id_path,
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikation_von,
                         h.edifact_format_version,

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
                         h.sort_path || substr('00000' || de.position, -5) || '-' AS sort_path,
                         h.id_path || de.id || '>'                                AS id_path,
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikation_von,
                         h.edifact_format_version,

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
                         h.sort_path || substr('00000' || c.position, -5) || '-' AS sort_path,
                         h.id_path || c.value || '>'                             AS id_path,
                         h.pruefidentifikator,
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.beschreibung,
                         h.kommunikation_von,
                         h.edifact_format_version,

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

SELECT hex(randomblob(16)) AS id, *
FROM hierarchy
ORDER BY anwendungsfall_pk, sort_path;



CREATE UNIQUE INDEX idx_hierarchy_id ON ahb_hierarchy_materialized (id);
CREATE INDEX idx_hierarchy_afpk ON ahb_hierarchy_materialized (anwendungsfall_pk);
CREATE INDEX idx_hierarchy_sort ON ahb_hierarchy_materialized (anwendungsfall_pk, sort_path);
CREATE INDEX idx_hierarchy_type ON ahb_hierarchy_materialized (type);
CREATE INDEX idx_hierarchy_pruefidentifikator ON ahb_hierarchy_materialized (pruefidentifikator);
CREATE INDEX idx_hierarchy_format ON ahb_hierarchy_materialized (format);
CREATE INDEX idx_hierarchy_versionsnummer ON ahb_hierarchy_materialized (versionsnummer);
CREATE INDEX idx_hierarchy_gueltig_von ON ahb_hierarchy_materialized (gueltig_von);
CREATE INDEX idx_hierarchy_gueltig_bis ON ahb_hierarchy_materialized (gueltig_bis);
CREATE INDEX idx_hierarchy_beschreibung ON ahb_hierarchy_materialized (beschreibung);
CREATE INDEX idx_hierarchy_kommunikation_von ON ahb_hierarchy_materialized (kommunikation_von);
CREATE INDEX idx_hierarchy_edifact_format_version ON ahb_hierarchy_materialized (edifact_format_version);
CREATE INDEX idx_hierarchy_segmentgroup_id ON ahb_hierarchy_materialized (segmentgroup_id);
CREATE INDEX idx_hierarchy_segmentgroup_name ON ahb_hierarchy_materialized (segmentgroup_name);
CREATE INDEX idx_hierarchy_segmentgroup_position ON ahb_hierarchy_materialized (segmentgroup_position);
CREATE INDEX idx_hierarchy_segment_id ON ahb_hierarchy_materialized (segment_id);
CREATE INDEX idx_hierarchy_segment_name ON ahb_hierarchy_materialized (segment_name);
CREATE INDEX idx_hierarchy_segment_number ON ahb_hierarchy_materialized (segment_number);
CREATE INDEX idx_hierarchy_segment_position ON ahb_hierarchy_materialized (segment_position);
CREATE INDEX idx_hierarchy_dataelementgroup_id ON ahb_hierarchy_materialized (dataelementgroup_id);
CREATE INDEX idx_hierarchy_dataelementgroup_name ON ahb_hierarchy_materialized (dataelementgroup_name);
CREATE INDEX idx_hierarchy_dataelementgroup_position ON ahb_hierarchy_materialized (dataelementgroup_position);
CREATE INDEX idx_hierarchy_dataelement_id ON ahb_hierarchy_materialized (dataelement_id);
CREATE INDEX idx_hierarchy_dataelement_name ON ahb_hierarchy_materialized (dataelement_name);
CREATE INDEX idx_hierarchy_dataelement_position ON ahb_hierarchy_materialized (dataelement_position);
CREATE INDEX idx_hierarchy_dataelement_ahb_status ON ahb_hierarchy_materialized (dataelement_ahb_status);
CREATE INDEX idx_hierarchy_code_id ON ahb_hierarchy_materialized (code_id);
CREATE INDEX idx_hierarchy_code_name ON ahb_hierarchy_materialized (code_name);
CREATE INDEX idx_hierarchy_code_description ON ahb_hierarchy_materialized (code_description);
CREATE INDEX idx_hierarchy_code_value ON ahb_hierarchy_materialized (code_value);
CREATE INDEX idx_hierarchy_code_ahb_status ON ahb_hierarchy_materialized (code_ahb_status);
CREATE INDEX idx_hierarchy_code_position ON ahb_hierarchy_materialized (code_position);
CREATE INDEX idx_hierarchy_path ON ahb_hierarchy_materialized (path);
CREATE INDEX idx_hierarchy_id_path ON ahb_hierarchy_materialized (id_path);
CREATE UNIQUE INDEX idx_hierarchy_path_per_ahb ON ahb_hierarchy_materialized (path, pruefidentifikator, edifact_format_version);
CREATE UNIQUE INDEX idx_hierarchy_id_path_per_ahb ON ahb_hierarchy_materialized (id_path, pruefidentifikator, edifact_format_version);

