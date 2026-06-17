SELECT

    id,

    service_code,

    service_name,

    description

FROM service_master

WHERE active = TRUE

ORDER BY service_name;