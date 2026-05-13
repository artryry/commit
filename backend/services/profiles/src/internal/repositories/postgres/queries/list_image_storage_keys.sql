SELECT storage_key
FROM images
WHERE id = ANY($1)
  AND user_id = $2;
