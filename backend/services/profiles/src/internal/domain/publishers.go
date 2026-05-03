package domain

import "context"

type ProfileUpdatedPublisher interface {
	PublishProfileUpdated(ctx context.Context, userID int64, extra map[string]any) error
}
