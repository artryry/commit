package kafka

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type Event struct {
	EventID    string          `json:"event_id"`
	EventType  string          `json:"event_type"`
	OccurredAt time.Time       `json:"occurred_at"`
	Payload    json.RawMessage `json:"payload"`
}

type userIDPayload struct {
	ID int64 `json:"id"`
}

func newEvent(eventType string, payload map[string]any) (Event, error) {
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
