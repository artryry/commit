package services

import (
	"context"

	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
	"github.com/artryry/commit/backend/services/profiles/src/internal/logger"
)

type ProfileService struct {
	profileRepository domain.ProfileRepository
	tagService        TagService
}

func NewProfileService(profileRepository domain.ProfileRepository) *ProfileService {
	return &ProfileService{
		profileRepository: profileRepository,
	}
}

func (s *ProfileService) CreateProfile(
	ctx context.Context,
	userId int64,
) error {
	err := s.profileRepository.CreateProfile(ctx, userId)
	if err != nil {
		return err
	}
	logger.Info("Profile created successfully", "user_id", userId)

	return nil
}

func (s *ProfileService) GetProfiles(
	ctx context.Context,
	userIds []int64,
) ([]*domain.Profile, error) {
	return s.profileRepository.GetProfiles(ctx, userIds)
}

func (s *ProfileService) GetProfilesWithFilter(
	ctx context.Context,
	filter domain.ProfileFilter,
) ([]*domain.Profile, error) {
	return s.profileRepository.GetProfilesWithFilter(ctx, filter)
}

func (s *ProfileService) GetProfile(
	ctx context.Context,
	userId int64,
) (*domain.Profile, error) {
	userIds := []int64{userId}

	profiles, err := s.GetProfiles(ctx, userIds)
	if err != nil {
		return nil, err
	} else if len(profiles) == 0 {
		return nil, domain.ErrProfileNotFound{UserId: userId}
	}

	return profiles[0], nil
}

func (s *ProfileService) FillProfile(ctx context.Context, profile *domain.Profile) error {
	err := s.profileRepository.FillProfile(ctx, profile)
	if err != nil {
		return err
	}
	logger.Info("Profile filled successfully", "user_id", profile.UserId)

	return nil
}

func (s *ProfileService) UpdateProfile(ctx context.Context, profile *domain.Profile) error {
	err := s.profileRepository.UpdateProfile(ctx, profile)
	if err != nil {
		return err
	}
	logger.Info("Profile updated successfully", "user_id", profile.UserId)

	return nil
}

func (s *ProfileService) DeleteProfile(ctx context.Context, userId int64) error {
	err := s.profileRepository.DeleteProfile(ctx, userId)
	if err != nil {
		return err
	}
	logger.Info("Profile deleted successfully", "user_id", userId)

	return nil
}
