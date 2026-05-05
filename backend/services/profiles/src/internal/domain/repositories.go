package domain

import "context"

type ProfileRepository interface {
	CreateProfile(ctx context.Context, userId int64) error
	FillProfile(ctx context.Context, profile *Profile) error
	GetProfiles(ctx context.Context, userIds []int64) ([]*Profile, error)
	GetProfilesWithFilter(ctx context.Context, filter ProfileFilter) ([]*Profile, error)
	UpdateProfile(ctx context.Context, profile *Profile) error
	DeleteProfile(ctx context.Context, userId int64) error
}

type ImageRepository interface {
	CreateImage(ctx context.Context, userID int64, storageKey string) (*Image, error)
	DeleteImages(ctx context.Context, imageIds []int64, userId int64) error
}

type TagRepository interface {
	CreateTags(ctx context.Context, tags []string) error
	AttachTags(ctx context.Context, userId int64, tags []string) error
	DetachTags(ctx context.Context, userId int64, tags []string) error
}
