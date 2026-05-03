package postgres

import (
	"context"

	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
	"github.com/jackc/pgx/v5/pgxpool"
)

type ImageRepository struct {
	db *pgxpool.Pool
}

func NewImageRepository(db *pgxpool.Pool) *ImageRepository {
	return &ImageRepository{
		db: db,
	}
}

func (r *ImageRepository) CreateImage(
	ctx context.Context,
	userID int64,
	storageKey string,
) (*domain.Image, error) {
	var image domain.Image

	err := r.db.QueryRow(
		ctx,
		createImageQuery,
		userID,
		storageKey,
	).Scan(
		&image.Id,
		&image.UserId,
		&image.StorageKey,
		&image.CreatedAt,
	)

	if err != nil {
		return nil, err
	}

	return &image, nil
}

func (r *ImageRepository) DeleteImages(
	ctx context.Context,
	imageId []int64,
	userId int64,
) error {
	_, err := r.db.Exec(
		ctx,
		createImageQuery,
		imageId,
		userId,
	)
	if err != nil {
		return err
	}

	return nil
}
