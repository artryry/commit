package postgres

import (
	"context"
	"encoding/json"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/artryry/commit/services/profiles/src/internal/config"
	"github.com/artryry/commit/services/profiles/src/internal/domain"
)

type ProfileRepository struct {
	cfg *config.Config
	db  *pgxpool.Pool
}

func NewProfileRepository(cfg *config.Config, db *pgxpool.Pool) *ProfileRepository {
	initQueries(cfg)

	return &ProfileRepository{
		cfg: cfg,
		db:  db,
	}
}

func (r *ProfileRepository) CreateProfile(ctx context.Context, profile *domain.Profile) error {
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

func (r *ProfileRepository) UpdateProfile(ctx context.Context, profile *domain.Profile) error {
	return nil
}

func (r *ProfileRepository) DeleteProfile(ctx context.Context, userId int64) error {
	return nil
}
