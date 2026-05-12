INSERT INTO profiles (user_id)
VALUES ($1)
ON CONFLICT (user_id) DO NOTHING;
