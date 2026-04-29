CREATE TABLE IF NOT EXISTS image_moderation (
    image_id BIGINT PRIMARY KEY,

    status moderation_status NOT NULL DEFAULT 'pending',

    reason TEXT,

    checked_at TIMESTAMP,

    CONSTRAINT fk_image_moderation_image
        FOREIGN KEY(image_id)
        REFERENCES images(id)
        ON DELETE CASCADE
);