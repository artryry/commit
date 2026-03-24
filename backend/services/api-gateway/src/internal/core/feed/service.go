package service

import (
	"context"

	"github.com/Ryryr0/commit/api-gateway/internal/dto"
)

type FeedService interface {
	GetFeed(ctx context.Context) ([]*dto.Feed, error)
}

func NewFeedService() FeedService {
	return &feedService{}
}

type feedService struct {
}

func (s *feedService) GetFeed(ctx context.Context) ([]*dto.Feed, error) {
	return nil, nil
}
