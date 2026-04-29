CREATE TABLE IF NOT EXISTS profiles (
    user_id BIGINT PRIMARY KEY,

    username VARCHAR(30) NOT NULL UNIQUE,

    birth_day DATE NOT NULL,

    gender gender NOT NULL,

    bio TEXT,

    search_for TEXT,

    city VARCHAR(100),

    avatar_image_id BIGINT,

    relationship_type relationship_type,

    sign VARCHAR(30),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);