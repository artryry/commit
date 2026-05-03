CREATE TABLE IF NOT EXISTS profiles (
    user_id BIGINT PRIMARY KEY,

    username VARCHAR(30),

    birth_day DATE,

    gender gender,

    bio TEXT,

    search_for TEXT,

    city VARCHAR(100),

    avatar_image_id BIGINT,

    relationship_type relationship_type DEFAULT 'unspecified',

    sign VARCHAR(30),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);