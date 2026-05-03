UPDATE profiles
SET
    username = $1,
    avatar_image_id = $2,
    bio = $3,
    city = $4,
    search_for = $5,
    relationship_type = $6,
    birth_day = $7,
    gender = $8,
    sign = $9,
    updated_at = NOW()
WHERE user_id = $10;
