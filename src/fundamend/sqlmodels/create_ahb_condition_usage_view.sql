-- Assume that materialize_ahb_view.sql, create_ahbtabellen_view.sql and create_and_fill_ahb_condition_usage_table(...)
-- have been executed already. The view answers "on which lines of which AHB is condition X used (directly or via)?"

DROP TABLE IF EXISTS v_ahb_condition_usages; -- this is because sqlmodel tries to create a table first... it doesn't know that this is just a view. bit dirty but ok.
DROP VIEW IF EXISTS v_ahb_condition_usages;

CREATE VIEW v_ahb_condition_usages AS
SELECT l.id || u.id                       as id, -- one line can use the same key directly and via UB, so the line id alone is not unique
       u.edifact_format_version            as format_version, -- from u (not l), so that the lookup index on ahb_condition_usages can be used,
       u.format                           as format,
       l.pruefidentifikator               as pruefidentifikator,
       l.description                      as description,
       l.direction                        as direction,
       l.segmentgroup_key                 as segmentgroup_key,
       l.segment_code                     as segment_code,
       l.data_element                     as data_element,
       l.qualifier                        as qualifier,
       l.line_name                        as line_name,
       l.line_ahb_status                  as line_ahb_status,
       l.sort_path                        as sort_path,
       l.anwendungshandbuch_primary_key   as anwendungshandbuch_primary_key,
       u.condition_key                    as condition_key,
       u.key_type                         as key_type,
       NULLIF(u.via, '')                  as via -- NULL for direct use
-- line_ahb_status is already trimmed in ahb_hierarchy_materialized, like v_ahbtabellen joins ahb_expressions (no TRIM)
FROM ahb_condition_usages AS u
         CROSS JOIN v_ahbtabellen AS l -- CROSS JOIN forces sqlite to start at u (filtered by the lookup index)
              ON u.edifact_format_version = l.format_version
                  AND u.format = l.format
                  AND u.anwendungshandbuch_primary_key = l.anwendungshandbuch_primary_key
                  AND u.expression = l.line_ahb_status;
