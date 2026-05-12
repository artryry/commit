package repository

import (
	"context"
	"database/sql"
	"errors"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

var ErrSelfSwipe = errors.New("cannot swipe on yourself")

type RecordResult struct {
	NewMatchID *int64
}

type Repository struct {
	db *pgxpool.Pool
}

func New(db *pgxpool.Pool) *Repository {
	return &Repository{db: db}
}

func normalizePair(a, b int64) (first, sec int64) {
	if a < b {
		return a, b
	}
	return b, a
}

func (r *Repository) RecordSwipe(ctx context.Context, viewer, target int64, liked bool) (*RecordResult, error) {
	if viewer == target {
		return nil, ErrSelfSwipe
	}
	first, sec := normalizePair(viewer, target)

	tx, err := r.db.Begin(ctx)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err != nil {
			_ = tx.Rollback(ctx)
		}
	}()

	_, err = tx.Exec(ctx, `
INSERT INTO swipes (
	first_user_id, sec_user_id,
	first_user_answer, sec_user_answer,
	first_answered_at, sec_answered_at,
	updated_at
) VALUES (
	$1::bigint, $2::bigint,
	CASE WHEN $3::bigint = $1::bigint THEN $4::boolean ELSE NULL::boolean END,
	CASE WHEN $3::bigint = $2::bigint THEN $4::boolean ELSE NULL::boolean END,
	CASE WHEN $3::bigint = $1::bigint THEN NOW() ELSE NULL::timestamptz END,
	CASE WHEN $3::bigint = $2::bigint THEN NOW() ELSE NULL::timestamptz END,
	NOW()
)
ON CONFLICT (first_user_id, sec_user_id) DO UPDATE SET
	first_user_answer = CASE WHEN $3::bigint = swipes.first_user_id THEN $4::boolean ELSE swipes.first_user_answer END,
	sec_user_answer = CASE WHEN $3::bigint = swipes.sec_user_id THEN $4::boolean ELSE swipes.sec_user_answer END,
	first_answered_at = CASE WHEN $3::bigint = swipes.first_user_id THEN NOW() ELSE swipes.first_answered_at END,
	sec_answered_at = CASE WHEN $3::bigint = swipes.sec_user_id THEN NOW() ELSE swipes.sec_answered_at END,
	updated_at = NOW()
`, first, sec, viewer, liked)
	if err != nil {
		return nil, err
	}

	var fa, sa sql.NullBool
	err = tx.QueryRow(ctx, `
SELECT first_user_answer, sec_user_answer
FROM swipes
WHERE first_user_id = $1::bigint AND sec_user_id = $2::bigint
`, first, sec).Scan(&fa, &sa)
	if err != nil {
		return nil, err
	}

	out := &RecordResult{}
	if fa.Valid && sa.Valid && fa.Bool && sa.Bool {
		var mid int64
		err = tx.QueryRow(ctx, `
INSERT INTO matches (first_user_id, sec_user_id)
VALUES ($1::bigint, $2::bigint)
ON CONFLICT (first_user_id, sec_user_id) DO NOTHING
RETURNING id
`, first, sec).Scan(&mid)
		if err == nil {
			out.NewMatchID = &mid
		} else if !errors.Is(err, pgx.ErrNoRows) {
			return nil, err
		}
	}

	err = tx.Commit(ctx)
	if err != nil {
		return nil, err
	}

	return out, nil
}

func (r *Repository) ListMatchedUserIDs(ctx context.Context, userID int64) ([]int64, error) {
	rows, err := r.db.Query(ctx, `
SELECT CASE WHEN m.first_user_id = $1::bigint THEN m.sec_user_id ELSE m.first_user_id END
FROM matches m
WHERE m.first_user_id = $1::bigint OR m.sec_user_id = $1::bigint
ORDER BY m.created_at DESC
`, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var ids []int64
	for rows.Next() {
		var id int64
		if err := rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	if ids == nil {
		ids = []int64{}
	}
	return ids, nil
}

// ListIncomingLikesUserIDs returns other users who liked viewer (their answer toward the pair is like),
// excluding rows that are already mutual matches (both users liked).
func (r *Repository) ListIncomingLikesUserIDs(ctx context.Context, viewer int64) ([]int64, error) {
	rows, err := r.db.Query(ctx, `
SELECT CASE WHEN s.first_user_id = $1::bigint THEN s.sec_user_id ELSE s.first_user_id END
FROM swipes s
WHERE (
	(s.first_user_id = $1::bigint AND s.sec_user_answer IS TRUE)
	OR (s.sec_user_id = $1::bigint AND s.first_user_answer IS TRUE)
)
AND NOT (COALESCE(s.first_user_answer, false) AND COALESCE(s.sec_user_answer, false))
ORDER BY s.updated_at DESC
`, viewer)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var ids []int64
	for rows.Next() {
		var id int64
		if err := rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	if ids == nil {
		ids = []int64{}
	}
	return ids, nil
}
