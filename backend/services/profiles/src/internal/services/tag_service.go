package services

import (
	"context"

	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
)

type TagService struct {
	tagRepository domain.TagRepository
}

func NewTagService(tagRepository domain.TagRepository) *TagService {
	return &TagService{
		tagRepository: tagRepository,
	}
}

func (s *TagService) AttachTags(ctx context.Context, userId int64, tags []string) error {
	err := s.tagRepository.CreateTags(ctx, tags)
	if err != nil {
		return err
	}

	return s.tagRepository.AttachTags(ctx, userId, tags)
}

func (s *TagService) DetachTags(ctx context.Context, userId int64, tags []string) error {
	return s.tagRepository.DetachTags(ctx, userId, tags)
}
