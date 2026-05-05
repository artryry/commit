package handlers

import (
	"context"
	"strings"
	"time"

	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
	"github.com/artryry/commit/backend/services/profiles/src/internal/logger"
	"github.com/artryry/commit/backend/services/profiles/src/internal/services"
	pb "github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc/proto/gen"
)

type ProfileHandler struct {
	pb.UnimplementedProfileServiceServer

	profileService *services.ProfileService
	imageService   *services.ImageService
	tagService     *services.TagService
	profileUpdated domain.ProfileUpdatedPublisher
}

func NewProfileHandler(
	profileService *services.ProfileService,
	imageService *services.ImageService,
	tagService *services.TagService,
	profileUpdated domain.ProfileUpdatedPublisher,
) *ProfileHandler {
	return &ProfileHandler{
		profileService: profileService,
		imageService:   imageService,
		tagService:     tagService,
		profileUpdated: profileUpdated,
	}
}

func (h *ProfileHandler) emitProfileUpdated(ctx context.Context, userID int64, extra map[string]any) {
	if h.profileUpdated == nil {
		return
	}
	if err := h.profileUpdated.PublishProfileUpdated(ctx, userID, extra); err != nil {
		logger.Error("publish profile.updated", "err", err, "user_id", userID)
	}
}

func (h *ProfileHandler) CreateProfile(
	ctx context.Context,
	req *pb.CreateProfileRequest,
) (*pb.CreateProfileResponse, error) {
	profileData := req.GetProfile()
	if profileData == nil {
		return &pb.CreateProfileResponse{Success: false}, nil
	}

	profile := &domain.Profile{
		UserId:           profileData.GetUserId(),
		Username:         profileData.GetUsername(),
		Avatar:           &domain.Image{Id: profileData.GetAvatarImage().GetId()},
		Bio:              profileData.GetBio(),
		City:             profileData.GetCity(),
		SearchFor:        profileData.GetSearchFor(),
		RelationshipType: relationshipTypeToDomain(profileData.GetRelationshipType()),
		Sign:             profileData.GetSign(),
		Birthday:         time.Unix(profileData.GetBirthday(), 0),
		Gender:           genderToDomain(profileData.GetGender()),
	}

	if err := h.profileService.FillProfile(ctx, profile); err != nil {
		return nil, err
	}

	h.emitProfileUpdated(ctx, profile.UserId, map[string]any{"source": "fill_profile"})

	return &pb.CreateProfileResponse{Success: true}, nil
}

func (h *ProfileHandler) GetProfile(
	ctx context.Context,
	req *pb.GetProfileRequest,
) (*pb.GetProfileResponse, error) {
	profile, err := h.profileService.GetProfile(ctx, req.GetUserId())

	if err != nil {
		return nil, err
	}

	return &pb.GetProfileResponse{
		ProfileData: toFullProfile(profile),
	}, nil
}

func (h *ProfileHandler) GetProfiles(
	ctx context.Context,
	req *pb.GetProfilesRequest,
) (*pb.GetProfilesResponse, error) {
	profiles, err := h.profileService.GetProfiles(ctx, req.GetUserIds())
	if err != nil {
		return nil, err
	}

	result := make([]*pb.ShortProfile, 0, len(profiles))
	for _, profile := range profiles {
		result = append(result, toShortProfile(profile))
	}

	return &pb.GetProfilesResponse{
		ProfilesData: result,
	}, nil
}

func (h *ProfileHandler) GetProfilesWithFilter(
	ctx context.Context,
	req *pb.GetProfilesWithFilterRequest,
) (*pb.GetProfilesWithFilterResponse, error) {
	filter := domain.ProfileFilter{
		UserIDs: req.GetUserIds(),
		Tags:    req.GetTags(),
	}

	if req.RelationshipType != nil {
		if db := relationshipTypeProtoToDBEnum(*req.RelationshipType); db != nil {
			filter.RelationshipType = db
		}
	}
	if req.AgeFrom != nil {
		filter.AgeFrom = req.AgeFrom
	}
	if req.AgeTo != nil {
		filter.AgeTo = req.AgeTo
	}
	if req.City != nil {
		filter.City = req.City
	}
	if req.Sign != nil {
		filter.Sign = req.Sign
	}

	profiles, err := h.profileService.GetProfilesWithFilter(ctx, filter)
	if err != nil {
		return nil, err
	}

	result := make([]*pb.ShortProfile, 0, len(profiles))
	for _, profile := range profiles {
		result = append(result, toShortProfile(profile))
	}

	return &pb.GetProfilesWithFilterResponse{
		ProfilesData: result,
	}, nil
}

func (h *ProfileHandler) UpdateProfile(
	ctx context.Context,
	req *pb.UpdateProfileRequest,
) (*pb.UpdateProfileResponse, error) {
	current, err := h.profileService.GetProfile(ctx, req.GetUserId())
	if err != nil {
		return nil, err
	}

	updated := *current

	if req.Username != nil {
		updated.Username = req.GetUsername()
	}
	if req.AvatarImageId != nil {
		updated.Avatar = &domain.Image{Id: req.GetAvatarImageId()}
	}
	if req.Bio != nil {
		updated.Bio = req.GetBio()
	}
	if req.City != nil {
		updated.City = req.GetCity()
	}
	if req.SearchFor != nil {
		updated.SearchFor = req.GetSearchFor()
	}
	if req.RelationshipType != nil {
		updated.RelationshipType = relationshipTypeToDomain(*req.RelationshipType)
	}

	if err := h.profileService.UpdateProfile(ctx, &updated); err != nil {
		return nil, err
	}

	latest, err := h.profileService.GetProfile(ctx, req.GetUserId())
	if err != nil {
		return nil, err
	}

	h.emitProfileUpdated(ctx, req.GetUserId(), map[string]any{"source": "update_profile"})

	return &pb.UpdateProfileResponse{
		ProfileData: toFullProfile(latest),
	}, nil
}

func (h *ProfileHandler) UploadProfileImage(
	ctx context.Context,
	req *pb.UploadProfileImageRequest,
) (*pb.UploadProfileImageResponse, error) {
	imageData := req.GetImage()
	image, err := h.imageService.CreateProfileImage(ctx, req.GetUserId(), &imageData)
	if err != nil {
		return nil, err
	}

	return &pb.UploadProfileImageResponse{
		UserId: req.GetUserId(),
		Image:  toPBImage(image),
	}, nil
}

func (h *ProfileHandler) DeleteProfileImages(
	ctx context.Context,
	req *pb.DeleteProfileImagesRequest,
) (*pb.DeleteProfileImagesResponse, error) {
	// Current proto does not contain requester id, so owner check can't be enforced here yet.
	if err := h.imageService.DeleteProfileImages(ctx, req.GetImageIds(), 0); err != nil {
		return nil, err
	}

	return &pb.DeleteProfileImagesResponse{
		Success: true,
	}, nil
}

func (h *ProfileHandler) AttachProfileTags(
	ctx context.Context,
	req *pb.AddProfileTagsRequest,
) (*pb.AddProfileTagsResponse, error) {
	if err := h.tagService.AttachTags(ctx, req.GetUserId(), req.GetTags()); err != nil {
		return nil, err
	}

	return &pb.AddProfileTagsResponse{
		Success: true,
	}, nil
}

func (h *ProfileHandler) DetachProfileTags(
	ctx context.Context,
	req *pb.DetachProfileTagsRequest,
) (*pb.DetachProfileTagsResponse, error) {
	if err := h.tagService.DetachTags(ctx, req.GetUserId(), req.GetTags()); err != nil {
		return nil, err
	}

	return &pb.DetachProfileTagsResponse{
		Success: true,
	}, nil
}

func toShortProfile(profile *domain.Profile) *pb.ShortProfile {
	return &pb.ShortProfile{
		UserId:      profile.UserId,
		Username:    profile.Username,
		AvatarImage: toPBImage(profile.Avatar),
		Bio:         profile.Bio,
		Age:         profile.Age,
		Sign:        profile.Sign,
		City:        profile.City,
		Tags:        profile.Tags,
		Images:      toPBImages(profile.Images),
	}
}

func toFullProfile(profile *domain.Profile) *pb.FullProfile {
	return &pb.FullProfile{
		UserId:           profile.UserId,
		Username:         profile.Username,
		AvatarImage:      toPBImage(profile.Avatar),
		Bio:              profile.Bio,
		Age:              profile.Age,
		Sign:             profile.Sign,
		City:             profile.City,
		RelationshipType: relationshipTypeToPB(profile.RelationshipType),
		SearchFor:        profile.SearchFor,
		Tags:             profile.Tags,
		Images:           toPBImages(profile.Images),
	}
}

func toPBImages(images []*domain.Image) []*pb.Image {
	result := make([]*pb.Image, 0, len(images))
	for _, image := range images {
		result = append(result, toPBImage(image))
	}

	return result
}

func toPBImage(image *domain.Image) *pb.Image {
	if image == nil {
		return nil
	}

	return &pb.Image{
		Id:       image.Id,
		Url:      image.StorageKey,
		CreateAt: image.CreatedAt.Unix(),
	}
}

func relationshipTypeToPB(value domain.RelationshipType) pb.RelationshipType {
	switch strings.ToUpper(string(value)) {
	case "FRIENDSHIP":
		return pb.RelationshipType_SEARCH_FOR_FRIENDSHIP
	case "RELATIONSHIP":
		return pb.RelationshipType_SEARCH_FOR_RELATIONSHIP
	case "NETWORKING":
		return pb.RelationshipType_SEARCH_FOR_NETWORKING
	default:
		return pb.RelationshipType_SEARCH_FOR_UNSPECIFIED
	}
}

func relationshipTypeToDomain(value pb.RelationshipType) domain.RelationshipType {
	switch value {
	case pb.RelationshipType_SEARCH_FOR_FRIENDSHIP:
		return domain.SearchForFriendship
	case pb.RelationshipType_SEARCH_FOR_RELATIONSHIP:
		return domain.SearchForRelationship
	case pb.RelationshipType_SEARCH_FOR_NETWORKING:
		return domain.SearchForNetworking
	default:
		return domain.SearchForUnspecified
	}
}

func genderToDomain(value pb.Gender) domain.Gender {
	switch value {
	case pb.Gender_FEMALE:
		return domain.GenderFemale
	case pb.Gender_MALE:
		return domain.GenderMale
	default:
		return domain.GenderMale
	}
}

// relationshipTypeProtoToDBEnum maps proto enum to Postgres relationship_type labels.
func relationshipTypeProtoToDBEnum(v pb.RelationshipType) *string {
	switch v {
	case pb.RelationshipType_SEARCH_FOR_FRIENDSHIP:
		s := "friendship"
		return &s
	case pb.RelationshipType_SEARCH_FOR_RELATIONSHIP:
		s := "relationship"
		return &s
	case pb.RelationshipType_SEARCH_FOR_UNSPECIFIED:
		s := "unspecified"
		return &s
	case pb.RelationshipType_SEARCH_FOR_NETWORKING:
		return nil
	default:
		return nil
	}
}
