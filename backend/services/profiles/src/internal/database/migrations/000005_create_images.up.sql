CREATE TABLE IF NOT EXISTS images (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    storage_key TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_images_profile
        FOREIGN KEY(user_id)
        REFERENCES profiles(user_id)
        ON DELETE CASCADE
);