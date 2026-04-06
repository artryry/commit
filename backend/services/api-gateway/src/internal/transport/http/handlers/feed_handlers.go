package handlers

import (
	"encoding/json"
	"net/http"

	service "github.com/artryry/commit/services/api-gateway/src/internal/core/feed"
)

type FeedHandlers struct {
	feedService service.FeedService
}

func NewFeedHandlers(feedService service.FeedService) *FeedHandlers {
	return &FeedHandlers{feedService: feedService}
}

func (h *FeedHandlers) GetFeed(w http.ResponseWriter, r *http.Request) {
	feed, err := h.feedService.GetFeed(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(feed)
}
