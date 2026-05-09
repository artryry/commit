CREATE TABLE IF NOT EXISTS matches (
    id BIGSERIAL PRIMARY KEY,
    first_user_id BIGINT NOT NULL,
    sec_user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT matches_ordered_pair CHECK (first_user_id < sec_user_id),
    CONSTRAINT matches_pair_unique UNIQUE (first_user_id, sec_user_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_users ON matches (first_user_id, sec_user_id);
