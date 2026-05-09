package kafka

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/google/uuid"
	kafkago "github.com/segmentio/kafka-go"

	"github.com/artryry/commit/backend/services/swipes/src/internal/config"
)

type Event struct {
	EventID    string          `json:"event_id"`
	EventType  string          `json:"event_type"`
	OccurredAt time.Time       `json:"occurred_at"`
	Payload    json.RawMessage `json:"payload"`
}

type Producer struct {
	writer *kafkago.Writer
	cfg    config.KafkaConfig
}

func NewProducer(cfg config.KafkaConfig) (*Producer, error) {
	if len(cfg.Brokers) == 0 {
		return nil, fmt.Errorf("kafka: no brokers")
	}
	w := &kafkago.Writer{
		Addr:                   kafkago.TCP(cfg.Brokers...),
		Balancer:               &kafkago.LeastBytes{},
		AllowAutoTopicCreation: true,
	}
	return &Producer{writer: w, cfg: cfg}, nil
}

func (p *Producer) Close() error {
	return p.writer.Close()
}

func newEnvelope(eventType string, payload map[string]any) (Event, error) {
	raw, err := json.Marshal(payload)
	if err != nil {
		return Event{}, err
	}
	return Event{
		EventID:    uuid.NewString(),
		EventType:  eventType,
		OccurredAt: time.Now().UTC(),
		Payload:    raw,
	}, nil
}

func (p *Producer) PublishSwipeCreated(ctx context.Context, viewerID, targetID int64, liked bool) error {
	ev, err := newEnvelope(p.cfg.SwipeCreatedTopic, map[string]any{
		"viewer_id":      viewerID,
		"target_user_id": targetID,
		"liked":          liked,
	})
	if err != nil {
		return err
	}
	body, err := json.Marshal(ev)
	if err != nil {
		return err
	}
	return p.writer.WriteMessages(ctx, kafkago.Message{
		Topic: p.cfg.SwipeCreatedTopic,
		Value: body,
	})
}

func (p *Producer) PublishMatchCreated(ctx context.Context, matchID, firstUserID, secUserID int64) error {
	ev, err := newEnvelope(p.cfg.MatchCreatedTopic, map[string]any{
		"match_id":       matchID,
		"first_user_id":  firstUserID,
		"sec_user_id":    secUserID,
	})
	if err != nil {
		return err
	}
	body, err := json.Marshal(ev)
	if err != nil {
		return err
	}
	return p.writer.WriteMessages(ctx, kafkago.Message{
		Topic: p.cfg.MatchCreatedTopic,
		Value: body,
	})
}
