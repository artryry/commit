package swipes

import (
	"context"

	swipespb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/swipes/proto/gen"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Client struct {
	conn   *grpc.ClientConn
	client swipespb.SwipesServiceClient
}

func New(address string) (*Client, error) {
	conn, err := grpc.NewClient(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, err
	}
	return &Client{
		conn:   conn,
		client: swipespb.NewSwipesServiceClient(conn),
	}, nil
}

func (c *Client) Close() error {
	if c == nil || c.conn == nil {
		return nil
	}
	return c.conn.Close()
}

func (c *Client) RecordSwipe(ctx context.Context, req *swipespb.RecordSwipeRequest) (*swipespb.RecordSwipeResponse, error) {
	return c.client.RecordSwipe(ctx, req)
}

func (c *Client) ListMatches(ctx context.Context, req *swipespb.ListMatchesRequest) (*swipespb.ListMatchesResponse, error) {
	return c.client.ListMatches(ctx, req)
}
