package tests

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
	"github.com/artryry/commit/backend/services/profiles/src/internal/services"
	handlers "github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc/handlers"
	pb "github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc/proto/gen"
)

type mockProfileRepo struct {
	createProfileFn           func(ctx context.Context, userID int64) error
	fillProfileFn             func(ctx context.Context, profile *domain.Profile) error
	getProfilesFn             func(ctx context.Context, userIDs []int64) ([]*domain.Profile, error)
	getProfilesWithFilterFn   func(ctx context.Context, filter domain.ProfileFilter) ([]*domain.Profile, error)
	updateProfileFn           func(ctx context.Context, profile *domain.Profile) error
	deleteProfileFn           func(ctx context.Context, userID int64) error
}

func (m *mockProfileRepo) CreateProfile(ctx context.Context, userID int64) error {
	if m.createProfileFn != nil {
		return m.createProfileFn(ctx, userID)
	}
	return nil
}

func (m *mockProfileRepo) FillProfile(ctx context.Context, profile *domain.Profile) error {
	if m.fillProfileFn != nil {
		return m.fillProfileFn(ctx, profile)
	}
	return nil
}

func (m *mockProfileRepo) GetProfiles(ctx context.Context, userIDs []int64) ([]*domain.Profile, error) {
	if m.getProfilesFn != nil {
		return m.getProfilesFn(ctx, userIDs)
	}
	return nil, nil
}

func (m *mockProfileRepo) GetProfilesWithFilter(ctx context.Context, filter domain.ProfileFilter) ([]*domain.Profile, error) {
	if m.getProfilesWithFilterFn != nil {
		return m.getProfilesWithFilterFn(ctx, filter)
	}
	return m.GetProfiles(ctx, filter.UserIDs)
}

func (m *mockProfileRepo) UpdateProfile(ctx context.Context, profile *domain.Profile) error {
	if m.updateProfileFn != nil {
		return m.updateProfileFn(ctx, profile)
	}
	return nil
}

func (m *mockProfileRepo) DeleteProfile(ctx context.Context, userID int64) error {
	if m.deleteProfileFn != nil {
		return m.deleteProfileFn(ctx, userID)
	}
	return nil
}

type mockImageRepo struct{}

func (m *mockImageRepo) CreateImage(ctx context.Context, userID int64, storageKey string) (*domain.Image, error) {
	return &domain.Image{Id: 1, UserId: userID, StorageKey: storageKey, CreatedAt: time.Now()}, nil
}

func (m *mockImageRepo) DeleteImages(ctx context.Context, imageIDs []int64, userID int64) error {
	return nil
}

type mockImageStorage struct{}

func (m *mockImageStorage) Upload(ctx context.Context, storageKey string, data []byte) error { return nil }
func (m *mockImageStorage) Delete(ctx context.Context, storageKey string) error               { return nil }

type mockTagRepo struct{}

func (m *mockTagRepo) CreateTags(ctx context.Context, tags []string) error                 { return nil }
func (m *mockTagRepo) AttachTags(ctx context.Context, userID int64, tags []string) error   { return nil }
func (m *mockTagRepo) DetachTags(ctx context.Context, userID int64, tags []string) error   { return nil }

type mockPublisher struct {
	calls []publishCall
}

type publishCall struct {
	userID int64
	extra  map[string]any
}

func (m *mockPublisher) PublishProfileUpdated(ctx context.Context, userID int64, extra map[string]any) error {
	m.calls = append(m.calls, publishCall{userID: userID, extra: extra})
	return nil
}

func TestProfileServiceGetProfileNotFound(t *testing.T) {
	svc := services.NewProfileService(&mockProfileRepo{
		getProfilesFn: func(ctx context.Context, userIDs []int64) ([]*domain.Profile, error) {
			return []*domain.Profile{}, nil
		},
	})

	_, err := svc.GetProfile(context.Background(), 99)
	if err == nil {
		t.Fatal("expected error for missing profile")
	}

	var notFound domain.ErrProfileNotFound
	if !errors.As(err, &notFound) {
		t.Fatalf("expected ErrProfileNotFound, got %T", err)
	}
}

func TestImageServiceCreateProfileImageUnsupportedType(t *testing.T) {
	svc := services.NewImageService(&mockImageRepo{}, &mockImageStorage{})
	data := []byte("not-an-image")

	_, err := svc.CreateProfileImage(context.Background(), 1, &data)
	if err == nil {
		t.Fatal("expected unsupported image type error")
	}

	var unsupported domain.ErrUnsupportedImageType
	if !errors.As(err, &unsupported) {
		t.Fatalf("expected ErrUnsupportedImageType, got %T", err)
	}
}

func TestProfileHandlerCreateProfilePublishesEvent(t *testing.T) {
	var filled *domain.Profile
	repo := &mockProfileRepo{
		fillProfileFn: func(ctx context.Context, profile *domain.Profile) error {
			filled = profile
			return nil
		},
	}
	pub := &mockPublisher{}

	h := handlers.NewProfileHandler(
		services.NewProfileService(repo),
		services.NewImageService(&mockImageRepo{}, &mockImageStorage{}),
		services.NewTagService(&mockTagRepo{}),
		pub,
	)

	req := &pb.CreateProfileRequest{
		Profile: &pb.ProfileRequest{
			UserId:   7,
			Username: "alice",
			Bio:      "bio",
			City:     "city",
			Sign:     "taurus",
			Gender:   pb.Gender_FEMALE,
		},
	}

	resp, err := h.CreateProfile(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !resp.Success {
		t.Fatal("expected success=true")
	}
	if filled == nil || filled.UserId != 7 || filled.Username != "alice" {
		t.Fatal("expected FillProfile to receive mapped profile data")
	}
	if len(pub.calls) != 1 {
		t.Fatalf("expected 1 publish call, got %d", len(pub.calls))
	}
	if pub.calls[0].extra["source"] != "fill_profile" {
		t.Fatalf("expected source=fill_profile, got %v", pub.calls[0].extra["source"])
	}
}

func TestProfileHandlerUpdateProfilePublishesEvent(t *testing.T) {
	current := &domain.Profile{
		UserId:           42,
		Username:         "old",
		Avatar:           &domain.Image{Id: 10},
		RelationshipType: domain.SearchForFriendship,
	}

	var updated *domain.Profile
	repo := &mockProfileRepo{
		getProfilesFn: func(ctx context.Context, userIDs []int64) ([]*domain.Profile, error) {
			return []*domain.Profile{current}, nil
		},
		updateProfileFn: func(ctx context.Context, profile *domain.Profile) error {
			updated = profile
			return nil
		},
	}
	pub := &mockPublisher{}

	h := handlers.NewProfileHandler(
		services.NewProfileService(repo),
		services.NewImageService(&mockImageRepo{}, &mockImageStorage{}),
		services.NewTagService(&mockTagRepo{}),
		pub,
	)

	newName := "new-name"
	_, err := h.UpdateProfile(context.Background(), &pb.UpdateProfileRequest{
		UserId:   42,
		Username: &newName,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if updated == nil || updated.Username != "new-name" {
		t.Fatal("expected UpdateProfile to be called with updated username")
	}
	if len(pub.calls) != 1 {
		t.Fatalf("expected 1 publish call, got %d", len(pub.calls))
	}
	if pub.calls[0].userID != 42 {
		t.Fatalf("expected userID=42, got %d", pub.calls[0].userID)
	}
	if pub.calls[0].extra["source"] != "update_profile" {
		t.Fatalf("expected source=update_profile, got %v", pub.calls[0].extra["source"])
	}
}
