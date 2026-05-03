package postgres

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

type TagRepository struct {
	db *pgxpool.Pool
}

func NewTagRepository(db *pgxpool.Pool) *TagRepository {
	return &TagRepository{
		db: db,
	}
}

func (r *TagRepository) CreateTags(
	ctx context.Context,
	tags []string,
) error {
	_, err := r.db.Exec(
		ctx,
		createTagsQuery,
		tags,
	)
	if err != nil {
		return err
	}

	return nil
}

func (r *TagRepository) AttachTags(
	ctx context.Context,
	userId int64,
	tags []string,
) error {
	_, err := r.db.Exec(
		ctx,
		attachTagsQuery,
		userId,
		tags,
	)
	if err != nil {
		return err
	}

	return nil
}

func (r *TagRepository) DetachTags(
	ctx context.Context,
	userId int64,
	tags []string,
) error {
	_, err := r.db.Exec(
		ctx,
		detachProfileTagsQuery,
		userId,
		tags,
	)
	if err != nil {
		return err
	}

	return nil
}
