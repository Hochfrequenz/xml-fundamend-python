-- Assume that materialize_ahb_view.sql has been executed already.
-- Then we can create another view on top of ahb_hierarchy_materialized.
-- This is especially useful for our ahbesser frontend (aka "AHB-Tabellen")

DROP TABLE IF EXISTS v_ahbtabellen; -- this is because sqlmodel tries to create a table first... it doesn't know that this is just a view. bit dirty but ok.
DROP VIEW IF EXISTS v_ahbtabellen;

CREATE VIEW v_ahbtabellen AS
WITH consolidated_ahm AS (SELECT id,
                                 anwendungshandbuch_primary_key,
                                 edifact_format_version,
                                 format,
                                 pruefidentifikator,
                                 path,
                                 id_path,
                                 kommunikation_von,
                                 beschreibung,
                                 segmentgroup_id,
                                 segment_id,
                                 is_on_uebertragungsdatei_level,
                                 dataelement_id,
                                 code_value,
                                 sort_path,
                                 trim(coalesce(code_ahb_status, coalesce(dataelement_ahb_status,
                                                                         coalesce(segment_ahb_status, segmentgroup_ahb_status))))     AS line_ahb_status,
                                 coalesce(code_name, coalesce(dataelement_name, coalesce(dataelementgroup_name,
                                                                                         coalesce(segment_name, segmentgroup_name)))) AS line_name,
                                 type                                                                                                 as line_type
                          FROM ahb_hierarchy_materialized ahm
                          WHERE ahm.TYPE != 'dataelementgroup'
                            AND (ahm.TYPE != 'dataelement' OR ahm.dataelement_ahb_status IS NOT NULL))

SELECT c.id                                  as id,
       c.anwendungshandbuch_primary_key      as anwendungshandbuch_primary_key,
       c.edifact_format_version              as format_version,
       c.format                              as format,
       c.pruefidentifikator                  as pruefidentifikator,
       c.path,
       c.id_path,
       c.kommunikation_von                   as direction,
       c.beschreibung                        as description,
       c.segmentgroup_id                     as segmentgroup_key, -- eg 'SG6'
       c.segment_id                          as segment_code,     -- e.g 'NAD'
       c.dataelement_id                      as data_element,     -- e.g 'D_3035'
       c.is_on_uebertragungsdatei_level      as is_on_uebertragungsdatei_level, -- true for UNA/UNB+UNZ, not for UNH
       --CASE
       --    WHEN dataelement_id IS NOT NULL THEN SUBSTR(dataelement_id, 3)
       --    END                                                                                              AS dataelement_without_leading_d_, -- e.g '3035'
       c.code_value                          as qualifier,
       c.line_ahb_status                     as line_ahb_status,                -- e.g. 'Muss [28] ∧ [64]'
       c.line_name                           as line_name,                      -- e.g. 'Datums- oder Uhrzeit- oder Zeitspannen-Format, Code' or 'Produkt-Daten für Lieferant relevant'
       c.line_type                           as line_type,
       c.sort_path                           as sort_path,
       NULLIF(ahe.node_texts, '')            as bedingung,
       NULLIF(ahe.ahbicht_error_message, '') as bedingungsfehler
FROM consolidated_ahm as c
         LEFT JOIN ahb_expressions as ahe -- if this table is missing, call create_and_fill_ahb_expression_table(...) first
                   ON ahe.edifact_format_version = c.edifact_format_version
                       AND ahe.format = c.format
                       AND ahe.expression = c.line_ahb_status;
