package recommendations

import (
	"context"

	recommendationpb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/recommendations/proto/gen"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type RecommendationClient struct {
	conn   *grpc.ClientConn
	client recommendationpb.RecommendationServiceClient
}

func NewRecommendationClient(address string) (*RecommendationClient, error) {
	conn, err := grpc.NewClient(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, err
	}

	return &RecommendationClient{
		conn:   conn,
		client: recommendationpb.NewRecommendationServiceClient(conn),
	}, nil
}

func (c *RecommendationClient) Close() error {
	if c == nil || c.conn == nil {
		return nil
	}
	return c.conn.Close()
}

func (c *RecommendationClient) GetRecommendationsForUser(ctx context.Context, req *recommendationpb.GetRecommendationsForUserRequest) (*recommendationpb.GetRecommendationsForUserResponse, error) {
	return c.client.GetRecommendationsForUser(ctx, req)
}

func (c *RecommendationClient) GetFilters(ctx context.Context, req *recommendationpb.GetFiltersRequest) (*recommendationpb.GetFiltersResponse, error) {
	return c.client.GetFilters(ctx, req)
}

func (c *RecommendationClient) SetFilters(ctx context.Context, req *recommendationpb.SetFiltersRequest) (*recommendationpb.SetFiltersResponse, error) {
	return c.client.SetFilters(ctx, req)
}
