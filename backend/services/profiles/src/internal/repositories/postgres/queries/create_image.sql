INSERT INTO images (
    user_id,
    storage_key,
)
VALUES (
    $1,
    $2,
)
RETURNING 
    id,
    user_id,
    storage_key,
    created_at;
    