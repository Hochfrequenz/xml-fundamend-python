-- Assume that materialize_ahb_view.sql has been executed already.
-- Then we can create another view on top of ahb_hierarchy_materialized.
-- This is especially useful for our ahbesser frontend (aka "AHB-Tabellen")

DROP TABLE IF EXISTS v_ahbtabellen; -- this is because sqlmodel tries to create a table first... it doesn't know that this is just a view. bit dirty but ok.
DROP VIEW IF EXISTS v_ahbtabellen;
CREATE VIEW v_ahbtabellen as
SELECT id                                                                                                   as id,
       edifact_format_version                                                                               as format_version,
       pruefidentifikator                                                                                   as pruefidentifikator,
       path,
       id_path,
       kommunikation_von                                                                                    as direction,
       beschreibung                                                                                         as description,
       'SG' || segmentgroup_id                                                                              as segmentgroup_key, -- eg 'SG6'
       segment_id                                                                                           as segment_code,     -- e.g 'NAD'
       dataelement_id                                                                                       as data_element,     -- e.g 'D_3035'
       --CASE
       --    WHEN dataelement_id IS NOT NULL THEN SUBSTR(dataelement_id, 3)
       --    END                                                                                              AS dataelement_without_leading_d_, -- e.g '3035'
       code_value                                                                                           as qualifier,

       coalesce(code_ahb_status, coalesce(dataelement_ahb_status,
                                          coalesce(segment_ahb_status, segmentgroup_ahb_status)))           as line_ahb_status,  -- e.g. 'Muss [28] ∧ [64]'
       coalesce(code_name, coalesce(dataelement_name, coalesce(dataelementgroup_name,
                                                               coalesce(segment_name, segmentgroup_name)))) as line_name,        -- e.g. 'Datums- oder Uhrzeit- oder Zeitspannen-Format, Code' or 'Produkt-Daten für Lieferant relevant'
       sort_path                                                                                            as sort_path
-- the bedingung column is still missing, but we'll solve this one separately
FROM ahb_hierarchy_materialized
WHERE type != 'dataelementgroup' and type!='dataelement';