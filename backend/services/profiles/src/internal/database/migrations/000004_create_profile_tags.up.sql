CREATE TABLE IF NOT EXISTS profiles_tags (
    user_id BIGINT NOT NULL,

    tag_id BIGINT NOT NULL,

    PRIMARY KEY(user_id, tag_id),

    CONSTRAINT fk_profiles_tags_profile
        FOREIGN KEY(user_id)
        REFERENCES profiles(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_profiles_tags_tag
        FOREIGN KEY(tag_id)
        REFERENCES tags(id)
        ON DELETE CASCADE
);