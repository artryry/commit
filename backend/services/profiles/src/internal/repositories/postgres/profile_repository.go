package postgres

import (
	"context"
	"encoding/json"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/artryry/commit/backend/services/profiles/src/internal/config"
	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
)

type ProfileRepository struct {
	db *pgxpool.Pool
}

func NewProfileRepository(cfg *config.Config, db *pgxpool.Pool) *ProfileRepository {
	initQueries(cfg)

	return &ProfileRepository{
		db: db,
	}
}

func (r *ProfileRepository) CreateProfile(
	ctx context.Context,
	userId int64,
) error {
	tx, err := r.db.Begin(ctx)
	if err != nil {
		return err
	}

	defer func() {
		if err != nil {
			_ = tx.Rollback(ctx)
		}
	}()

	_, err = tx.Exec(
		ctx,
		createProfileQuery,
		userId,
	)
	if err != nil {
		return err
	}

	err = tx.Commit(ctx)
	if err != nil {
		return err
	}

	return nil
}

func (r *ProfileRepository) FillProfile(
	ctx context.Context,
	profile *domain.Profile,
) error {
	_, err := r.db.Exec(
		ctx,
		fillProfileQuery,
		profile.Username,
		profile.Avatar.Id,
		profile.Bio,
		profile.City,
		profile.SearchFor,
		profile.RelationshipType,
		profile.Birthday,
		profile.Gender,
		profile.Sign,
		profile.UserId,
	)
	if err != nil {
		return err
	}

	return nil
}

func (r *ProfileRepository) GetProfiles(
	ctx context.Context,
	userIDs []int64,
) ([]*domain.Profile, error) {
	rows, err := r.db.Query(
		ctx,
		getProfilesQuery,
		userIDs,
	)
	if err != nil {
		return nil, err
	}

	defer rows.Close()

	var profiles []*domain.Profile

	for rows.Next() {
		var profile domain.Profile
		var imagesJSON []byte

		err := rows.Scan(
			&profile.UserId,
			&profile.Username,
			&profile.Avatar.Id,
			&profile.Bio,
			&profile.Age,
			&profile.Sign,
			&profile.City,
			&profile.SearchFor,
			&profile.RelationshipType,
			&profile.Tags,
			&imagesJSON,
		)
		if err != nil {
			return nil, err
		}

		var images []*domain.Image

		err = json.Unmarshal(
			imagesJSON,
			&images,
		)
		if err != nil {
			return nil, err
		}

		profile.Images = images

		for _, image := range images {
			if image.Id == profile.Avatar.Id {
				profile.Avatar = image
				break
			}
		}

		profiles = append(
			profiles,
			&profile,
		)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return profiles, nil
}

func (r *ProfileRepository) UpdateProfile(
	ctx context.Context,
	profile *domain.Profile,
) error {
	_, err := r.db.Exec(
		ctx,
		updateProfileQuery,
		profile.Username,
		profile.Avatar.Id,
		profile.Bio,
		profile.City,
		profile.SearchFor,
		profile.RelationshipType,

		profile.UserId,
	)
	if err != nil {
		return err
	}

	return nil
}

func (r *ProfileRepository) DeleteProfile(
	ctx context.Context,
	userId int64,
) error {
	_, err := r.db.Exec(
		ctx,
		deleteProfileQuery,
		userId,
	)
	if err != nil {
		return err
	}

	return nil
}
