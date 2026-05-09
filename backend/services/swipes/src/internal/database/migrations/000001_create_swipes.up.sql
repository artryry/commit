CREATE TABLE IF NOT EXISTS swipes (
    first_user_id BIGINT NOT NULL,
    sec_user_id BIGINT NOT NULL,
    first_user_answer BOOLEAN NULL,
    sec_user_answer BOOLEAN NULL,
    first_answered_at TIMESTAMPTZ NULL,
    sec_answered_at TIMESTAMPTZ NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (first_user_id, sec_user_id),
    CONSTRAINT swipes_ordered_pair CHECK (first_user_id < sec_user_id)
);

CREATE INDEX IF NOT EXISTS idx_swipes_updated ON swipes (updated_at);
