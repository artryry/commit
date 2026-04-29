package handlers

import (
	"context"

	"github.com/artryry/commit/services/profiles/src/internal/services"
	pb "github.com/artryry/commit/services/profiles/src/internal/transport/grpc/proto/gen"
)

type ProfileHandler struct {
	pb.UnimplementedProfileServiceServer

	service *services.ProfileService
}

func NewProfileHandler(
	service *services.ProfileService,
) *ProfileHandler {
	return &ProfileHandler{
		service: service,
	}
}

func (h *ProfileHandler) GetProfile(
	ctx context.Context,
	req *pb.GetProfileRequest,
) (*pb.ProfileResponse, error) {

	profile, err := h.service.GetProfile(
		ctx,
		req.UserId,
	)

	if err != nil {
		return nil, err
	}

	return &pb.ProfileResponse{
		Profile: &pb.FullProfile{
			UserId:   profile.ID,
			Username: profile.Username,
			AvatarImage: &pb.Image{
				Id:  profile.Avatar.Id,
				Url: profile.Avatar.Url,
			},
			Tags:             profile.Tags,
			Images:           getProfileImages(profile),
			Bio:              profile.Bio,
			City:             profile.City,
			Age:              profile.Age,
			Sign:             profile.Sign,
			RelationshipType: pb.RelationshipType(profile.RelationshipType),
			SearchFor:        profile.SerchFor,
		},
	}, nil
}

// TODO !!!!!!!!!!!!!!
func getProfileImages(profile *services.FullProfile) []*pb.Image {
	return []*pb.Image{
		{
			Id:  profile.Images[0].Id,
			Url: profile.Images[0].Url,
		},
	}
}
