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

func (r *ImageRepository) ListStorageKeysByImageIDs(
	ctx context.Context,
	userID int64,
	imageIDs []int64,
) ([]string, error) {
	if len(imageIDs) == 0 {
		return nil, nil
	}
	rows, err := r.db.Query(ctx, listImageStorageKeysQuery, imageIDs, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var keys []string
	for rows.Next() {
		var key string
		if err := rows.Scan(&key); err != nil {
			return nil, err
		}
		keys = append(keys, key)
	}
	return keys, rows.Err()
}

func (r *ImageRepository) DeleteImages(
	ctx context.Context,
	imageId []int64,
	userId int64,
) error {
	_, err := r.db.Exec(
		ctx,
		deleteImageQuery,
		imageId,
		userId,
	)
	if err != nil {
		return err
	}

	return nil
}
