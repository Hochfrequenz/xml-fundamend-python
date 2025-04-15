-- This SQLite script selects all ahb_status from various other tables into one common table.
-- There is a Pydantic model class for the 'ahb_expressions' table: AhbExpression

INSERT INTO ahb_expressions (id, edifact_format_version, format, pruefidentifikator, expression, node_texts, anwendungshandbuch_primary_key)
SELECT DISTINCT
    hex(randomblob(16)) AS id,
    edifact_format_version,
    format,
    pruefidentifikator,
    expression,
    '' AS node_texts, -- will be filled with the help of ahbicht in python
    anwendungshandbuch_primary_key
FROM (
    SELECT edifact_format_version,
           format,
           pruefidentifikator,
           segmentgroup_ahb_status AS expression,
           anwendungshandbuch_primary_key
    FROM ahb_hierarchy_materialized
    UNION ALL
    SELECT edifact_format_version,
           format,
           pruefidentifikator,
           segment_ahb_status AS expression,
           anwendungshandbuch_primary_key
    FROM ahb_hierarchy_materialized
    UNION ALL
    SELECT edifact_format_version,
           format,
           pruefidentifikator,
           dataelement_ahb_status AS expression,
           anwendungshandbuch_primary_key
    FROM ahb_hierarchy_materialized
    UNION ALL
    SELECT edifact_format_version,
           format,
           pruefidentifikator,
           code_ahb_status AS expression,
           anwendungshandbuch_primary_key
    FROM ahb_hierarchy_materialized
)
WHERE expression IS NOT NULL AND TRIM(expression) != ''
ORDER BY edifact_format_version, format, pruefidentifikator, expression;

-- Create indexes
CREATE INDEX idx_ahb_expressions_expression ON ahb_expressions (expression);
CREATE INDEX idx_ahb_expressions_metadata ON ahb_expressions (edifact_format_version, format, pruefidentifikator);
CREATE UNIQUE INDEX idx_ahb_expressions_metadata_expression ON ahb_expressions (edifact_format_version, format, pruefidentifikator, expression);