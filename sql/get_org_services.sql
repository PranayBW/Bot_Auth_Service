SELECT

    sm.id,

    sm.service_code,

    sm.service_name,

    sm.description

FROM organization_service_mapping osm

INNER JOIN service_master sm
    ON sm.id = osm.service_id

WHERE
    osm.organization_id = $1
    AND osm.active = TRUE
    AND sm.active = TRUE

ORDER BY sm.service_name;