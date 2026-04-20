package auth

import (
	"context"

	pb "github.com/artryry/commit/services/api-gateway/src/clients/auth/proto"
	"github.com/artryry/commit/services/api-gateway/src/internal/dto"

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

type Client struct {
	Conn   *grpc.ClientConn
	Client pb.AuthClient
}

func New(address string) (*Client, error) {
	conn, err := grpc.NewClient(address)
	if err != nil {
		return nil, err
	}

	return &Client{
		Conn:   conn,
		Client: pb.NewAuthClient(conn),
	}, nil
}

func (c *Client) Close() error {
	return c.Conn.Close()
}

func (c *Client) Authorize(ctx context.Context, req *dto.AuthRequest) (*AuthorizeResponse, error) {
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

func (c *Client) Register(ctx context.Context, req *dto.RegisterRequest) (*RegisterResponse, error) {
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

func (c *Client) Refresh(ctx context.Context, req *dto.RefreshRequest) (string, error) {
	pbRequest := &pb.RefreshRequest{
		RefreshToken: req.RefreshToken,
	}

	pbResponse, err := c.Client.Refresh(ctx, pbRequest)
	if err != nil {
		return "", err
	}

	return pbResponse.Jwt, nil
}

func (c *Client) Delete(ctx context.Context, req *dto.DeleteAccountRequest) (bool, error) {
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
