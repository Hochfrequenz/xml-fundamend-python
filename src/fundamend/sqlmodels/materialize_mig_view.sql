-- This SQLite script materializes the hierarchy of the MIG (Message Implementation Guide) into a table.
-- This allows for easy querying without 'unrolling' the recursive segment (group) hierarchy each time.
-- There is a Pydantic model class for the 'mig_hierarchy_materialized' table: MigHierarchyMaterialized

-- Drop previous materialized table if it exists
DROP TABLE IF EXISTS mig_hierarchy_materialized;

-- Materialize hierarchy for ALL MIGs
CREATE TABLE mig_hierarchy_materialized AS
WITH RECURSIVE

    ordered_roots AS (SELECT sg.primary_key,
                             sg.position,
                             'segment_group' AS type,
                             sg.id           AS root_id_text,
                             sg.name,
                             sg.status_std,
                             sg.status_specification,
                             sg.counter,
                             sg.level,
                             sg.max_rep_std,
                             sg.max_rep_specification,
                             sg.mig_primary_key,
                             NULL            AS number,
                             NULL            AS example,
                             NULL            AS description,
                             mig.format,
                             mig.versionsnummer,
                             mig.gueltig_von,
                             mig.gueltig_bis,
                             mig.edifact_format_version,
                             NULL            AS is_on_uebertragungsdatei_level
                      FROM migsegmentgroup sg
                               JOIN messageimplementationguide mig ON sg.mig_primary_key = mig.primary_key
                      WHERE sg.mig_primary_key IS NOT NULL

                      UNION ALL

                      SELECT s.primary_key,
                             s.position,
                             'segment' AS type,
                             s.id      AS root_id_text,
                             s.name,
                             s.status_std,
                             s.status_specification,
                             s.counter,
                             s.level,
                             s.max_rep_std,
                             s.max_rep_specification,
                             s.mig_primary_key,
                             s.number,
                             s.example,
                             s.description,
                             mig.format,
                             mig.versionsnummer,
                             mig.gueltig_von,
                             mig.gueltig_bis,
                             mig.edifact_format_version,
                             s.is_on_uebertragungsdatei_level
                      FROM migsegment s
                               JOIN messageimplementationguide mig ON s.mig_primary_key = mig.primary_key
                      WHERE s.segmentgroup_primary_key IS NULL
                        AND s.mig_primary_key IS NOT NULL),

    ordered_roots_with_order AS (SELECT *,
                                        ROW_NUMBER() OVER (
                                            PARTITION BY mig_primary_key
                                            ORDER BY position
                                            ) AS root_order
                                 FROM ordered_roots),

    root_hierarchy AS (SELECT o.mig_primary_key                                                    AS mig_pk,
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
                              o.format,
                              o.versionsnummer,
                              o.gueltig_von,
                              o.gueltig_bis,
                              o.edifact_format_version,
                              o.is_on_uebertragungsdatei_level,

                              -- Segment Group fields
                              CASE WHEN o.type = 'segment_group' THEN o.root_id_text ELSE NULL END AS segmentgroup_id,
                              CASE WHEN o.type = 'segment_group' THEN o.name ELSE NULL END         AS segmentgroup_name,
                              CASE WHEN o.type = 'segment_group' THEN o.status_std ELSE NULL END   AS segmentgroup_status_std,
                              CASE
                                  WHEN o.type = 'segment_group' THEN o.status_specification
                                  ELSE NULL END                                                    AS segmentgroup_status_specification,
                              CASE WHEN o.type = 'segment_group' THEN o.counter ELSE NULL END      AS segmentgroup_counter,
                              CASE WHEN o.type = 'segment_group' THEN o.level ELSE NULL END        AS segmentgroup_level,
                              CASE WHEN o.type = 'segment_group' THEN o.max_rep_std ELSE NULL END  AS segmentgroup_max_rep_std,
                              CASE
                                  WHEN o.type = 'segment_group' THEN o.max_rep_specification
                                  ELSE NULL END                                                    AS segmentgroup_max_rep_specification,
                              CASE WHEN o.type = 'segment_group' THEN o.position ELSE NULL END     AS segmentgroup_position,

                              -- Segment fields
                              CASE WHEN o.type = 'segment' THEN o.root_id_text ELSE NULL END       AS segment_id,
                              CASE WHEN o.type = 'segment' THEN o.name ELSE NULL END               AS segment_name,
                              CASE WHEN o.type = 'segment' THEN o.status_std ELSE NULL END         AS segment_status_std,
                              CASE
                                  WHEN o.type = 'segment' THEN o.status_specification
                                  ELSE NULL END                                                    AS segment_status_specification,
                              CASE WHEN o.type = 'segment' THEN o.counter ELSE NULL END            AS segment_counter,
                              CASE WHEN o.type = 'segment' THEN o.level ELSE NULL END              AS segment_level,
                              CASE WHEN o.type = 'segment' THEN o.number ELSE NULL END             AS segment_number,
                              CASE WHEN o.type = 'segment' THEN o.max_rep_std ELSE NULL END        AS segment_max_rep_std,
                              CASE
                                  WHEN o.type = 'segment' THEN o.max_rep_specification
                                  ELSE NULL END                                                    AS segment_max_rep_specification,
                              CASE WHEN o.type = 'segment' THEN o.example ELSE NULL END            AS segment_example,
                              CASE WHEN o.type = 'segment' THEN o.description ELSE NULL END        AS segment_description,
                              CASE WHEN o.type = 'segment' THEN o.position ELSE NULL END           AS segment_position,

                              -- Data Element Group fields (NULL at root level)
                              NULL                                                                 AS dataelementgroup_id,
                              NULL                                                                 AS dataelementgroup_name,
                              NULL                                                                 AS dataelementgroup_description,
                              NULL                                                                 AS dataelementgroup_status_std,
                              NULL                                                                 AS dataelementgroup_status_specification,
                              NULL                                                                 AS dataelementgroup_position,

                              -- Data Element fields (NULL at root level)
                              NULL                                                                 AS dataelement_id,
                              NULL                                                                 AS dataelement_name,
                              NULL                                                                 AS dataelement_description,
                              NULL                                                                 AS dataelement_status_std,
                              NULL                                                                 AS dataelement_status_specification,
                              NULL                                                                 AS dataelement_format_std,
                              NULL                                                                 AS dataelement_format_specification,
                              NULL                                                                 AS dataelement_position,

                              -- Code fields (NULL at root level)
                              NULL                                                                 AS code_id,
                              NULL                                                                 AS code_name,
                              NULL                                                                 AS code_description,
                              NULL                                                                 AS code_value,
                              NULL                                                                 AS code_position
                       FROM ordered_roots_with_order o),

    hierarchy AS (SELECT *
                  FROM root_hierarchy

                  UNION ALL

                  -- Nested segment groups (via link table)
                  SELECT h.mig_pk,
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
                         h.id_path || child.id || '>',
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.edifact_format_version,
                         h.is_on_uebertragungsdatei_level,

                         child.id,
                         child.name,
                         child.status_std,
                         child.status_specification,
                         child.counter,
                         child.level,
                         child.max_rep_std,
                         child.max_rep_specification,
                         child.position,

                         h.segment_id,
                         h.segment_name,
                         h.segment_status_std,
                         h.segment_status_specification,
                         h.segment_counter,
                         h.segment_level,
                         h.segment_number,
                         h.segment_max_rep_std,
                         h.segment_max_rep_specification,
                         h.segment_example,
                         h.segment_description,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_description,
                         h.dataelementgroup_status_std,
                         h.dataelementgroup_status_specification,
                         h.dataelementgroup_position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_description,
                         h.dataelement_status_std,
                         h.dataelement_status_specification,
                         h.dataelement_format_std,
                         h.dataelement_format_specification,
                         h.dataelement_position,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_position
                  FROM hierarchy h
                           JOIN migsegmentgrouplink link ON h.current_id = link.parent_id
                           JOIN migsegmentgroup child ON link.child_id = child.primary_key
                  WHERE h.type = 'segment_group'

                  UNION ALL

                  -- Segments within segment groups
                  SELECT h.mig_pk,
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
                         h.id_path || s.id || '>',
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.edifact_format_version,
                         s.is_on_uebertragungsdatei_level,

                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_status_std,
                         h.segmentgroup_status_specification,
                         h.segmentgroup_counter,
                         h.segmentgroup_level,
                         h.segmentgroup_max_rep_std,
                         h.segmentgroup_max_rep_specification,
                         h.segmentgroup_position,

                         s.id,
                         s.name,
                         s.status_std,
                         s.status_specification,
                         s.counter,
                         s.level,
                         s.number,
                         s.max_rep_std,
                         s.max_rep_specification,
                         s.example,
                         s.description,
                         s.position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_description,
                         h.dataelementgroup_status_std,
                         h.dataelementgroup_status_specification,
                         h.dataelementgroup_position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_description,
                         h.dataelement_status_std,
                         h.dataelement_status_specification,
                         h.dataelement_format_std,
                         h.dataelement_format_specification,
                         h.dataelement_position,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_position
                  FROM hierarchy h
                           JOIN migsegment s ON s.segmentgroup_primary_key = h.current_id
                  WHERE h.type = 'segment_group'

                  UNION ALL

                  -- Data element groups within segments
                  SELECT h.mig_pk,
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
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.edifact_format_version,
                         h.is_on_uebertragungsdatei_level,

                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_status_std,
                         h.segmentgroup_status_specification,
                         h.segmentgroup_counter,
                         h.segmentgroup_level,
                         h.segmentgroup_max_rep_std,
                         h.segmentgroup_max_rep_specification,
                         h.segmentgroup_position,

                         h.segment_id,
                         h.segment_name,
                         h.segment_status_std,
                         h.segment_status_specification,
                         h.segment_counter,
                         h.segment_level,
                         h.segment_number,
                         h.segment_max_rep_std,
                         h.segment_max_rep_specification,
                         h.segment_example,
                         h.segment_description,
                         h.segment_position,

                         deg.id,
                         deg.name,
                         deg.description,
                         deg.status_std,
                         deg.status_specification,
                         deg.position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_description,
                         h.dataelement_status_std,
                         h.dataelement_status_specification,
                         h.dataelement_format_std,
                         h.dataelement_format_specification,
                         h.dataelement_position,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_position
                  FROM hierarchy h
                           JOIN migdataelementgroup deg ON deg.segment_primary_key = h.current_id
                  WHERE h.type = 'segment'

                  UNION ALL

                  -- Data elements directly within segments (no group)
                  SELECT h.mig_pk,
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
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.edifact_format_version,
                         h.is_on_uebertragungsdatei_level,

                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_status_std,
                         h.segmentgroup_status_specification,
                         h.segmentgroup_counter,
                         h.segmentgroup_level,
                         h.segmentgroup_max_rep_std,
                         h.segmentgroup_max_rep_specification,
                         h.segmentgroup_position,

                         h.segment_id,
                         h.segment_name,
                         h.segment_status_std,
                         h.segment_status_specification,
                         h.segment_counter,
                         h.segment_level,
                         h.segment_number,
                         h.segment_max_rep_std,
                         h.segment_max_rep_specification,
                         h.segment_example,
                         h.segment_description,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_description,
                         h.dataelementgroup_status_std,
                         h.dataelementgroup_status_specification,
                         h.dataelementgroup_position,

                         de.id,
                         de.name,
                         de.description,
                         de.status_std,
                         de.status_specification,
                         de.format_std,
                         de.format_specification,
                         de.position,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_position
                  FROM hierarchy h
                           JOIN migdataelement de ON de.segment_primary_key = h.current_id
                  WHERE h.type = 'segment'
                    AND de.data_element_group_primary_key IS NULL

                  UNION ALL

                  -- Data elements within data element groups
                  SELECT h.mig_pk,
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
                         h.id_path || de.id || '>',
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.edifact_format_version,
                         h.is_on_uebertragungsdatei_level,

                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_status_std,
                         h.segmentgroup_status_specification,
                         h.segmentgroup_counter,
                         h.segmentgroup_level,
                         h.segmentgroup_max_rep_std,
                         h.segmentgroup_max_rep_specification,
                         h.segmentgroup_position,

                         h.segment_id,
                         h.segment_name,
                         h.segment_status_std,
                         h.segment_status_specification,
                         h.segment_counter,
                         h.segment_level,
                         h.segment_number,
                         h.segment_max_rep_std,
                         h.segment_max_rep_specification,
                         h.segment_example,
                         h.segment_description,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_description,
                         h.dataelementgroup_status_std,
                         h.dataelementgroup_status_specification,
                         h.dataelementgroup_position,

                         de.id,
                         de.name,
                         de.description,
                         de.status_std,
                         de.status_specification,
                         de.format_std,
                         de.format_specification,
                         de.position,

                         h.code_id,
                         h.code_name,
                         h.code_description,
                         h.code_value,
                         h.code_position
                  FROM hierarchy h
                           JOIN migdataelement de ON de.data_element_group_primary_key = h.current_id
                  WHERE h.type = 'dataelementgroup'

                  UNION ALL

                  -- Codes within data elements
                  SELECT h.mig_pk,
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
                         h.format,
                         h.versionsnummer,
                         h.gueltig_von,
                         h.gueltig_bis,
                         h.edifact_format_version,
                         h.is_on_uebertragungsdatei_level,

                         h.segmentgroup_id,
                         h.segmentgroup_name,
                         h.segmentgroup_status_std,
                         h.segmentgroup_status_specification,
                         h.segmentgroup_counter,
                         h.segmentgroup_level,
                         h.segmentgroup_max_rep_std,
                         h.segmentgroup_max_rep_specification,
                         h.segmentgroup_position,

                         h.segment_id,
                         h.segment_name,
                         h.segment_status_std,
                         h.segment_status_specification,
                         h.segment_counter,
                         h.segment_level,
                         h.segment_number,
                         h.segment_max_rep_std,
                         h.segment_max_rep_specification,
                         h.segment_example,
                         h.segment_description,
                         h.segment_position,

                         h.dataelementgroup_id,
                         h.dataelementgroup_name,
                         h.dataelementgroup_description,
                         h.dataelementgroup_status_std,
                         h.dataelementgroup_status_specification,
                         h.dataelementgroup_position,

                         h.dataelement_id,
                         h.dataelement_name,
                         h.dataelement_description,
                         h.dataelement_status_std,
                         h.dataelement_status_specification,
                         h.dataelement_format_std,
                         h.dataelement_format_specification,
                         h.dataelement_position,

                         c.primary_key,
                         c.name,
                         c.description,
                         c.value,
                         c.position
                  FROM hierarchy h
                           JOIN migcode c ON c.data_element_primary_key = h.current_id
                  WHERE h.type = 'dataelement')

SELECT hex(randomblob(16)) AS id,
       *,
       -- Computed columns for easier querying
       trim(
               coalesce(
                       code_name,
                       dataelement_name,
                       dataelementgroup_name,
                       segment_name,
                       segmentgroup_name
               )
       )                   AS line_name,
       trim(
               coalesce(
                       dataelement_status_std,
                       dataelementgroup_status_std,
                       segment_status_std,
                       segmentgroup_status_std
               )
       )                   AS line_status_std,
       trim(
               coalesce(
                       dataelement_status_specification,
                       dataelementgroup_status_specification,
                       segment_status_specification,
                       segmentgroup_status_specification
               )
       )                   AS line_status_specification
FROM hierarchy
ORDER BY mig_pk, sort_path;


-- Create indexes for efficient querying
CREATE UNIQUE INDEX idx_mig_hierarchy_id ON mig_hierarchy_materialized (id);
CREATE INDEX idx_mig_hierarchy_mig_pk ON mig_hierarchy_materialized (mig_pk);
CREATE INDEX idx_mig_hierarchy_mig_pk_sort ON mig_hierarchy_materialized (mig_pk, sort_path);
CREATE INDEX idx_mig_hierarchy_type ON mig_hierarchy_materialized (type);
CREATE INDEX idx_mig_hierarchy_format ON mig_hierarchy_materialized (format);
CREATE INDEX idx_mig_hierarchy_format_version ON mig_hierarchy_materialized (format, edifact_format_version);
CREATE INDEX idx_mig_hierarchy_versionsnummer ON mig_hierarchy_materialized (versionsnummer);
CREATE INDEX idx_mig_hierarchy_gueltig_von ON mig_hierarchy_materialized (gueltig_von);
CREATE INDEX idx_mig_hierarchy_gueltig_bis ON mig_hierarchy_materialized (gueltig_bis);
CREATE INDEX idx_mig_hierarchy_edifact_format_version ON mig_hierarchy_materialized (edifact_format_version);

-- Segment group indexes
CREATE INDEX idx_mig_hierarchy_segmentgroup_id ON mig_hierarchy_materialized (segmentgroup_id);
CREATE INDEX idx_mig_hierarchy_segmentgroup_name ON mig_hierarchy_materialized (segmentgroup_name);
CREATE INDEX idx_mig_hierarchy_segmentgroup_position ON mig_hierarchy_materialized (segmentgroup_position);

-- Segment indexes
CREATE INDEX idx_mig_hierarchy_segment_id ON mig_hierarchy_materialized (segment_id);
CREATE INDEX idx_mig_hierarchy_segment_name ON mig_hierarchy_materialized (segment_name);
CREATE INDEX idx_mig_hierarchy_segment_number ON mig_hierarchy_materialized (segment_number);
CREATE INDEX idx_mig_hierarchy_segment_position ON mig_hierarchy_materialized (segment_position);

-- Data element group indexes
CREATE INDEX idx_mig_hierarchy_dataelementgroup_id ON mig_hierarchy_materialized (dataelementgroup_id);
CREATE INDEX idx_mig_hierarchy_dataelementgroup_name ON mig_hierarchy_materialized (dataelementgroup_name);
CREATE INDEX idx_mig_hierarchy_dataelementgroup_position ON mig_hierarchy_materialized (dataelementgroup_position);

-- Data element indexes
CREATE INDEX idx_mig_hierarchy_dataelement_id ON mig_hierarchy_materialized (dataelement_id);
CREATE INDEX idx_mig_hierarchy_dataelement_name ON mig_hierarchy_materialized (dataelement_name);
CREATE INDEX idx_mig_hierarchy_dataelement_position ON mig_hierarchy_materialized (dataelement_position);

-- Code indexes
CREATE INDEX idx_mig_hierarchy_code_id ON mig_hierarchy_materialized (code_id);
CREATE INDEX idx_mig_hierarchy_code_name ON mig_hierarchy_materialized (code_name);
CREATE INDEX idx_mig_hierarchy_code_value ON mig_hierarchy_materialized (code_value);
CREATE INDEX idx_mig_hierarchy_code_position ON mig_hierarchy_materialized (code_position);

-- Path indexes
CREATE INDEX idx_mig_hierarchy_path ON mig_hierarchy_materialized (path);
CREATE INDEX idx_mig_hierarchy_id_path ON mig_hierarchy_materialized (id_path);
CREATE INDEX idx_mig_hierarchy_sort ON mig_hierarchy_materialized (sort_path);

-- Computed column indexes
CREATE INDEX idx_mig_line_name ON mig_hierarchy_materialized (line_name);
CREATE INDEX idx_mig_line_status_std ON mig_hierarchy_materialized (line_status_std);
CREATE INDEX idx_mig_line_status_specification ON mig_hierarchy_materialized (line_status_specification);

-- Append position to id_path only where duplicates exist (to ensure uniqueness)
UPDATE mig_hierarchy_materialized
SET id_path = id_path || '@' || sort_path
WHERE id IN (SELECT h1.id
             FROM mig_hierarchy_materialized h1
             WHERE EXISTS (SELECT 1
                           FROM mig_hierarchy_materialized h2
                           WHERE h2.id_path = h1.id_path
                             AND h2.format = h1.format
                             AND (h2.edifact_format_version = h1.edifact_format_version OR
                                  (h2.edifact_format_version IS NULL AND h1.edifact_format_version IS NULL))
                             AND h2.id != h1.id));

-- Append position to path only where duplicates exist (to ensure uniqueness for diff view matching)
UPDATE mig_hierarchy_materialized
SET path = path || ' @' || sort_path
WHERE id IN (SELECT h1.id
             FROM mig_hierarchy_materialized h1
             WHERE EXISTS (SELECT 1
                           FROM mig_hierarchy_materialized h2
                           WHERE h2.path = h1.path
                             AND h2.format = h1.format
                             AND (h2.edifact_format_version = h1.edifact_format_version OR
                                  (h2.edifact_format_version IS NULL AND h1.edifact_format_version IS NULL))
                             AND h2.id != h1.id));

-- Unique indexes for diff view support
CREATE UNIQUE INDEX idx_mig_hierarchy_id_path_per_mig ON mig_hierarchy_materialized (edifact_format_version, format, id_path);
CREATE UNIQUE INDEX idx_mig_hierarchy_path_per_mig ON mig_hierarchy_materialized (edifact_format_version, format, path);
