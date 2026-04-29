package domain

import "context"

type ProfileRepository interface {
	CreateProfile(ctx context.Context, profile *Profile) error
	GetProfiles(ctx context.Context, userIds []int64) ([]Profile, error)
	UpdateProfile(ctx context.Context, profile *Profile) error
	DeleteProfile(ctx context.Context, userId int64) error
}

type ImageRepository interface {
	CreateProfileImage(ctx context.Context, image *Image) error
	GetProfileImages(ctx context.Context, userId int64) ([]Image, error)
	DeleteProfileImages(ctx context.Context, imageIds []int64) error
}
