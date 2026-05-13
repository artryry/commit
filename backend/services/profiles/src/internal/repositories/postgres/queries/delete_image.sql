DELETE FROM images
WHERE id = ANY($1)
AND ($2::bigint = 0 OR user_id = $2);
