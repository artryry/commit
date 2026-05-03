package kafka

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/artryry/commit/backend/services/profiles/src/internal/config"
	kafkago "github.com/segmentio/kafka-go"
)

type Producer struct {
	writer *kafkago.Writer
	topic  string
}

func NewProducer(cfg config.KafkaConfig) (*Producer, error) {
	if len(cfg.Brokers) == 0 {
		return nil, fmt.Errorf("kafka: no brokers configured")
	}
	if cfg.ProfileUpdatedEventTopic == "" {
		return nil, fmt.Errorf("kafka: profile updated topic is empty")
	}

	w := &kafkago.Writer{
		Addr:                   kafkago.TCP(cfg.Brokers...),
		Topic:                  cfg.ProfileUpdatedEventTopic,
		Balancer:               &kafkago.LeastBytes{},
		AllowAutoTopicCreation: true,
	}

	return &Producer{writer: w, topic: cfg.ProfileUpdatedEventTopic}, nil
}

func (p *Producer) PublishProfileUpdated(ctx context.Context, userID int64, extra map[string]any) error {
	payload := map[string]any{
		"user_id": userID,
	}
	for k, v := range extra {
		payload[k] = v
	}
	ev, err := newEvent(p.topic, payload)
	if err != nil {
		return err
	}
	body, err := json.Marshal(ev)
	if err != nil {
		return err
	}
	return p.writer.WriteMessages(ctx, kafkago.Message{Value: body})
}

func (p *Producer) Close() error {
	return p.writer.Close()
}
