package auth

import (
	"context"

	"github.com/artryry/commit/services/api-gateway/src/internal/dto"
	pb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/auth/proto"

	"google.golang.org/grpc"
)

type AuthorizeResponse struct {
	JWT          string
	RefreshToken string
}

type RegisterResponse struct {
	JWT          string
	RefreshToken string
}

type GRPCClient struct {
	Conn   *grpc.ClientConn
	Client pb.AuthClient
}

func New(address string) (*GRPCClient, error) {
	conn, err := grpc.NewClient(address)
	if err != nil {
		return nil, err
	}

	return &GRPCClient{
		Conn:   conn,
		Client: pb.NewAuthClient(conn),
	}, nil
}

func (c *GRPCClient) Close() error {
	return c.Conn.Close()
}

func (c *GRPCClient) Authorize(ctx context.Context, req *dto.AuthRequest) (*AuthorizeResponse, error) {
	pbRequest := &pb.AuthorizeRequest{
		Email:    req.Email,
		Password: req.Password,
	}

	pbResponse, err := c.Client.Authorize(ctx, pbRequest)
	if err != nil {
		return nil, err
	}

	return &AuthorizeResponse{
		JWT:          pbResponse.Jwt,
		RefreshToken: pbResponse.RefreshToken,
	}, nil
}

func (c *GRPCClient) Register(ctx context.Context, req *dto.RegisterRequest) (*RegisterResponse, error) {
	pbRequest := &pb.RegisterRequest{
		Email:    req.Email,
		Password: req.Password,
	}

	pbResponse, err := c.Client.Register(ctx, pbRequest)
	if err != nil {
		return nil, err
	}

	return &RegisterResponse{
		JWT:          pbResponse.Jwt,
		RefreshToken: pbResponse.RefreshToken,
	}, nil
}

func (c *GRPCClient) Refresh(ctx context.Context, req *dto.RefreshRequest) (string, error) {
	pbRequest := &pb.RefreshRequest{
		RefreshToken: req.RefreshToken,
	}

	pbResponse, err := c.Client.Refresh(ctx, pbRequest)
	if err != nil {
		return "", err
	}

	return pbResponse.Jwt, nil
}

func (c *GRPCClient) Delete(ctx context.Context, req *dto.DeleteAccountRequest) (bool, error) {
	pbRequest := &pb.DeleteRequest{
		Jwt:          req.JWT,
		RefreshToken: req.RefreshToken,
	}

	_, err := c.Client.Delete(ctx, pbRequest)
	if err != nil {
		return false, err
	}

	return true, nil
}
