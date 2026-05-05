package profiles

import (
	"context"

	profilepb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/profiles/proto/gen"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type ProfileClient struct {
	conn   *grpc.ClientConn
	client profilepb.ProfileServiceClient
}

func NewProfileClient(address string) (*ProfileClient, error) {
	conn, err := grpc.NewClient(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, err
	}

	return &ProfileClient{
		conn:   conn,
		client: profilepb.NewProfileServiceClient(conn),
	}, nil
}

func (c *ProfileClient) Close() error {
	if c == nil || c.conn == nil {
		return nil
	}

	return c.conn.Close()
}

func (c *ProfileClient) GetProfile(ctx context.Context, req *profilepb.GetProfileRequest) (*profilepb.GetProfileResponse, error) {
	return c.client.GetProfile(ctx, req)
}

func (c *ProfileClient) GetProfiles(ctx context.Context, req *profilepb.GetProfilesRequest) (*profilepb.GetProfilesResponse, error) {
	return c.client.GetProfiles(ctx, req)
}

func (c *ProfileClient) GetProfilesWithFilter(ctx context.Context, req *profilepb.GetProfilesWithFilterRequest) (*profilepb.GetProfilesWithFilterResponse, error) {
	return c.client.GetProfilesWithFilter(ctx, req)
}

func (c *ProfileClient) UpdateProfile(ctx context.Context, req *profilepb.UpdateProfileRequest) (*profilepb.UpdateProfileResponse, error) {
	return c.client.UpdateProfile(ctx, req)
}

func (c *ProfileClient) UploadProfileImage(ctx context.Context, req *profilepb.UploadProfileImageRequest) (*profilepb.UploadProfileImageResponse, error) {
	return c.client.UploadProfileImage(ctx, req)
}

func (c *ProfileClient) DeleteProfileImages(ctx context.Context, req *profilepb.DeleteProfileImagesRequest) (*profilepb.DeleteProfileImagesResponse, error) {
	return c.client.DeleteProfileImages(ctx, req)
}

func (c *ProfileClient) AttachProfileTags(ctx context.Context, req *profilepb.AddProfileTagsRequest) (*profilepb.AddProfileTagsResponse, error) {
	return c.client.AttachProfileTags(ctx, req)
}

func (c *ProfileClient) DetachProfileTags(ctx context.Context, req *profilepb.DetachProfileTagsRequest) (*profilepb.DetachProfileTagsResponse, error) {
	return c.client.DetachProfileTags(ctx, req)
}
