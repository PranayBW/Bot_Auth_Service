SELECT

    id,

    service_code,

    service_name,

    description

FROM service_master

WHERE service_code = %(service_code)s
AND active = TRUE;