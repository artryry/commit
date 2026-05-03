package domain

import "context"

type ImageStorage interface {
	Upload(ctx context.Context, storageKey string, data []byte) error
	Delete(ctx context.Context, storageKey string) error
}
