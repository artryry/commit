package service

import (
	"context"

	"github.com/artryry/commit/backend/services/swipes/src/internal/kafka"
	"github.com/artryry/commit/backend/services/swipes/src/internal/logger"
	"github.com/artryry/commit/backend/services/swipes/src/internal/repository"
)

type Service struct {
	repo *repository.Repository
	pub  *kafka.Producer
}

func New(repo *repository.Repository, pub *kafka.Producer) *Service {
	return &Service{repo: repo, pub: pub}
}

func (s *Service) RecordSwipe(ctx context.Context, viewer, target int64, liked bool) error {
	res, err := s.repo.RecordSwipe(ctx, viewer, target, liked)
	if err != nil {
		return err
	}

	if err := s.pub.PublishSwipeCreated(ctx, viewer, target, liked); err != nil {
		logger.Error("publish swipe.created", "err", err)
	}

	if res != nil && res.NewMatchID != nil {
		first, sec := normalizePair(viewer, target)
		if err := s.pub.PublishMatchCreated(ctx, *res.NewMatchID, first, sec); err != nil {
			logger.Error("publish match.created", "err", err)
		}
	}

	return nil
}

func normalizePair(a, b int64) (first, sec int64) {
	if a < b {
		return a, b
	}
	return b, a
}

func (s *Service) ListMatchedUserIDs(ctx context.Context, userID int64) ([]int64, error) {
	return s.repo.ListMatchedUserIDs(ctx, userID)
}

func (s *Service) ListIncomingLikesUserIDs(ctx context.Context, userID int64) ([]int64, error) {
	return s.repo.ListIncomingLikesUserIDs(ctx, userID)
}
