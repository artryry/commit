INSERT INTO profiles_tags (
    user_id,
    tag_id
)
SELECT DISTINCT
    $1::bigint,
    t.id
FROM tags t
WHERE t.name = ANY($2::text[])
ON CONFLICT (user_id, tag_id) DO NOTHING;
