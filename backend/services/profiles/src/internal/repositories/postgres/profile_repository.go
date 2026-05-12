package postgres

import (
	"context"
	"database/sql"
	"encoding/json"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
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
	var avatarID any
	if profile.Avatar != nil && profile.Avatar.Id != 0 {
		avatarID = profile.Avatar.Id
	}

	_, err := r.db.Exec(
		ctx,
		fillProfileQuery,
		profile.Username,
		avatarID,
		profile.Bio,
		profile.City,
		profile.SearchFor,
		relationshipTypeToPG(profile.RelationshipType),
		profile.Birthday,
		genderToPG(profile.Gender),
		profile.Sign,
		profile.UserId,
	)
	if err != nil {
		return err
	}

	return nil
}

func genderToPG(g domain.Gender) string {
	if g == domain.GenderFemale {
		return "female"
	}
	return "male"
}

func relationshipTypeToPG(rt domain.RelationshipType) string {
	switch strings.ToUpper(string(rt)) {
	case "FRIENDSHIP":
		return "friendship"
	case "RELATIONSHIP":
		return "relationship"
	case "NETWORKING":
		// Postgres enum has no networking value; closest allowed label.
		return "unspecified"
	default:
		return "unspecified"
	}
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

	return scanProfileRows(rows)
}

func (r *ProfileRepository) GetProfilesWithFilter(
	ctx context.Context,
	filter domain.ProfileFilter,
) ([]*domain.Profile, error) {
	if len(filter.UserIDs) == 0 {
		return []*domain.Profile{}, nil
	}

	var rel any
	if filter.RelationshipType != nil {
		rel = *filter.RelationshipType
	}

	var ageFrom any
	if filter.AgeFrom != nil {
		ageFrom = *filter.AgeFrom
	}

	var ageTo any
	if filter.AgeTo != nil {
		ageTo = *filter.AgeTo
	}

	var city any
	if filter.City != nil {
		city = *filter.City
	}

	var sign any
	if filter.Sign != nil {
		sign = *filter.Sign
	}

	var tags any = []string{}
	if len(filter.Tags) > 0 {
		tags = filter.Tags
	}

	var partnerGender any
	if filter.PartnerGender != nil {
		partnerGender = *filter.PartnerGender
	}

	rows, err := r.db.Query(
		ctx,
		getProfilesWithFilterQuery,
		filter.UserIDs,
		rel,
		ageFrom,
		ageTo,
		city,
		sign,
		tags,
		partnerGender,
	)
	if err != nil {
		return nil, err
	}

	return scanProfileRows(rows)
}

// profileImageRow matches JSON from get_profiles*.sql (keys id, url, created_at as Unix seconds).
type profileImageRow struct {
	ID        int64  `json:"id"`
	URL       string `json:"url"`
	CreatedAt int64  `json:"created_at"`
}

func parseProfileImagesJSON(imagesJSON []byte) ([]*domain.Image, error) {
	if len(imagesJSON) == 0 || string(imagesJSON) == "null" {
		return []*domain.Image{}, nil
	}
	var rows []profileImageRow
	if err := json.Unmarshal(imagesJSON, &rows); err != nil {
		return nil, err
	}
	out := make([]*domain.Image, 0, len(rows))
	for _, r := range rows {
		out = append(out, &domain.Image{
			Id:         r.ID,
			StorageKey: r.URL,
			CreatedAt:  time.Unix(r.CreatedAt, 0).UTC(),
		})
	}
	return out, nil
}

func scanProfileRows(rows pgx.Rows) ([]*domain.Profile, error) {
	defer rows.Close()

	var profiles []*domain.Profile

	for rows.Next() {
		var profile domain.Profile
		var imagesJSON []byte
		var avatarID sql.NullInt64
		var birthDay sql.NullTime

		err := rows.Scan(
			&profile.UserId,
			&profile.Username,
			&avatarID,
			&profile.Bio,
			&profile.Age,
			&birthDay,
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

		if birthDay.Valid {
			t := birthDay.Time.UTC()
			y, m, d := t.Date()
			profile.Birthday = time.Date(y, m, d, 0, 0, 0, 0, time.UTC)
		}

		if avatarID.Valid {
			profile.Avatar = &domain.Image{Id: avatarID.Int64}
		}

		var images []*domain.Image

		images, err = parseProfileImagesJSON(imagesJSON)
		if err != nil {
			return nil, err
		}

		profile.Images = images

		for _, image := range images {
			if profile.Avatar != nil && image.Id == profile.Avatar.Id {
				profile.Avatar = image
				break
			}
		}

		profiles = append(profiles, &profile)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return profiles, nil
}

func (r *ProfileRepository) UpdateProfile(
	ctx context.Context,
	profile *domain.Profile,
) error {
	var avatarID any
	if profile.Avatar != nil && profile.Avatar.Id != 0 {
		avatarID = profile.Avatar.Id
	}

	_, err := r.db.Exec(
		ctx,
		updateProfileQuery,
		profile.Username,
		avatarID,
		profile.Bio,
		profile.City,
		profile.SearchFor,
		relationshipTypeToPG(profile.RelationshipType),

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
