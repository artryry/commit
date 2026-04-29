SELECT
    p.user_id,
    p.username,
    p.bio,
    DATE_PART('year', AGE(p.birth_day))::BIGINT AS age,
    p.sign,
    p.city,
    p.search_for,
    p.relationship_type,

    ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT t.name),
        NULL
    ) AS tags,

    COALESCE(
        JSON_AGG(
            DISTINCT JSONB_BUILD_OBJECT(
                'id', i.id,
                'url', i.storage_key
            )
        ) FILTER (WHERE i.id IS NOT NULL),
        '[]'
    ) AS images

FROM profiles p

LEFT JOIN profiles_tags pt
    ON pt.user_id = p.user_id

LEFT JOIN tags t
    ON t.id = pt.tag_id

LEFT JOIN images i
    ON i.user_id = p.user_id

WHERE p.user_id = ANY($1)

GROUP BY p.user_id

ORDER BY p.user_id;
