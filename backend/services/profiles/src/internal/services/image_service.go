package services

import (
	"context"
	"fmt"
	"net/http"

	"github.com/artryry/commit/backend/services/profiles/src/internal/domain"
	"github.com/google/uuid"
)

type ImageService struct {
	imageRepository domain.ImageRepository
	imageStorage    domain.ImageStorage
}

func NewImageService(
	imageRepository domain.ImageRepository,
	imageStorage domain.ImageStorage,
) *ImageService {
	return &ImageService{
		imageRepository: imageRepository,
		imageStorage:    imageStorage,
	}
}

func (s *ImageService) CreateProfileImage(
	ctx context.Context,
	userId int64,
	data *[]byte,
) (*domain.Image, error) {
	extension, err := getImageExtension(*data)
	if err != nil {
		return nil, err
	}

	storageKey := fmt.Sprintf(
		"profiles/%d/%s%s",
		userId,
		uuid.NewString(),
		extension,
	)

	err = s.imageStorage.Upload(ctx, storageKey, *data)
	if err != nil {
		return nil, err
	}

	image, err := s.imageRepository.CreateImage(
		ctx,
		userId,
		storageKey,
	)
	if err != nil {
		return nil, err
	}

	return image, nil
}

func getImageExtension(data []byte) (string, error) {

	contentType := http.DetectContentType(data)

	switch contentType {

	case "image/jpeg":
		return ".jpg", nil

	case "image/png":
		return ".png", nil

	case "image/webp":
		return ".webp", nil

	default:
		return "", domain.ErrUnsupportedImageType{}
	}
}

func (s *ImageService) DeleteProfileImages(ctx context.Context, imageId []int64, userId int64) error {
	return s.imageRepository.DeleteImages(ctx, imageId, userId)
}
