package service

import (
	"context"

	"github.com/artryry/commit/services/api-gateway/src/internal/dto"
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
