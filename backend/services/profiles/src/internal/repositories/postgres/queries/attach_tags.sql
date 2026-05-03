INSERT INTO profiles_tags (
    user_id,
    tag_id
)
SELECT
    $1,
    t.id
FROM tags t
WHERE t.name = ANY($2);
