SELECT
    p.user_id,
    p.username,
    p.avatar_image_id,
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

WHERE
    p.user_id = ANY($1::bigint[])
    AND ($2::text IS NULL OR p.relationship_type = $2::relationship_type)
    AND ($3::bigint IS NULL OR DATE_PART('year', AGE(p.birth_day))::BIGINT >= $3)
    AND ($4::bigint IS NULL OR DATE_PART('year', AGE(p.birth_day))::BIGINT <= $4)
    AND ($5::text IS NULL OR p.city ILIKE '%' || $5::text || '%')
    AND ($6::text IS NULL OR p.sign ILIKE '%' || $6::text || '%')
    AND (
        $7 IS NULL OR cardinality($7::text[]) = 0 OR NOT EXISTS (
            SELECT 1
            FROM (
                SELECT DISTINCT unnest($7::text[]) AS tag
            ) req
            WHERE NOT EXISTS (
                SELECT 1
                FROM profiles_tags pt2
                JOIN tags t2 ON t2.id = pt2.tag_id
                WHERE pt2.user_id = p.user_id AND t2.name = req.tag
            )
        )
    )

GROUP BY p.user_id

ORDER BY p.user_id;
