package kafka

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/artryry/commit/backend/services/profiles/src/internal/config"
	"github.com/artryry/commit/backend/services/profiles/src/internal/logger"
	"github.com/artryry/commit/backend/services/profiles/src/internal/services"
	kafkago "github.com/segmentio/kafka-go"
)

type UserEventsConsumer struct {
	cfg            *config.Config
	profileService *services.ProfileService
}

func NewUserEventsConsumer(cfg *config.Config, profileService *services.ProfileService) *UserEventsConsumer {
	return &UserEventsConsumer{
		cfg:            cfg,
		profileService: profileService,
	}
}

func (c *UserEventsConsumer) Run(ctx context.Context) error {
	k := c.cfg.Kafka
	if len(k.Brokers) == 0 {
		return fmt.Errorf("kafka consumer: no brokers configured")
	}
	topics := []string{k.UserCreatedEventTopic, k.UserDeletedEventTopic}
	r := kafkago.NewReader(kafkago.ReaderConfig{
		Brokers:     k.Brokers,
		GroupID:     k.GroupID,
		GroupTopics: topics,
		MinBytes:    1,
		MaxBytes:    10e6,
	})
	defer r.Close()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		msg, err := r.ReadMessage(ctx)
		if err != nil {
			if ctx.Err() != nil {
				return ctx.Err()
			}
			logger.Error("kafka read failed", "err", err)
			continue
		}
		if err := c.handleMessage(ctx, msg); err != nil {
			logger.Error("kafka message handling failed", "err", err, "topic", msg.Topic, "offset", msg.Offset)
		}
	}
}

func (c *UserEventsConsumer) handleMessage(ctx context.Context, msg kafkago.Message) error {
	var env Event
	if err := json.Unmarshal(msg.Value, &env); err != nil {
		return fmt.Errorf("decode envelope: %w", err)
	}

	eventType := env.EventType
	if eventType == "" {
		eventType = msg.Topic
	}

	var payload userIDPayload
	if err := json.Unmarshal(env.Payload, &payload); err != nil {
		return fmt.Errorf("decode payload: %w", err)
	}

	switch eventType {
	case c.cfg.Kafka.UserCreatedEventTopic:
		return c.profileService.CreateProfile(ctx, payload.ID)
	case c.cfg.Kafka.UserDeletedEventTopic:
		return c.profileService.DeleteProfile(ctx, payload.ID)
	default:
		return nil
	}
}
