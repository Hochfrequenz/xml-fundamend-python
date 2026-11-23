-- Assume that materialize_ahb_view.sql, create_ahbtabellen_view.sql and create_and_fill_ahb_condition_usage_table(...)
-- have been executed already. The view answers "on which lines of which AHB is condition X used (directly or via)?"

DROP TABLE IF EXISTS v_ahb_condition_usages; -- this is because sqlmodel tries to create a table first... it doesn't know that this is just a view. bit dirty but ok.
DROP VIEW IF EXISTS v_ahb_condition_usages;

CREATE VIEW v_ahb_condition_usages AS
SELECT l.id || u.id                       as id, -- one line can use the same key directly and via UB, so the line id alone is not unique
       l.format_version                   as format_version,
       l.format                           as format,
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
FROM v_ahbtabellen AS l
         JOIN ahb_condition_usages AS u
              ON u.anwendungshandbuch_primary_key = l.anwendungshandbuch_primary_key
                  AND u.expression = TRIM(l.line_ahb_status);
