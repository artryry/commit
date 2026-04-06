package dto

import "encoding/json"

type RecommendationRequest struct {
	UserID string `json:"user_id"`
}

func (r *RecommendationRequest) ToJSON() ([]byte, error) {
	return json.Marshal(r)
}

type RecommendationResponse struct {
	IDs        []string `json:"ids"`
	NextCursor string   `json:"next_cursor"`
}

func (r *RecommendationResponse) ToJSON() ([]byte, error) {
	return json.Marshal(r)
}
