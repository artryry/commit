package dto

import "encoding/json"

type ProfileRequest struct {
	IDs []string `json:"ids"`
}

func (p *ProfileRequest) ToJSON() ([]byte, error) {
	return json.Marshal(p)
}

type ProfileResponse struct {
	ID                 string   `json:"id"`
	Name               string   `json:"name"`
	Age                int      `json:"age"`
	City               string   `json:"city"`
	Bio                string   `json:"bio"`
	Tags               []string `json:"tags"`
	ProfileImagesURL   string   `json:"profile_images_url"`
	CompatibilityScore float64  `json:"compatibility_score"`
	CompatibilityText  string   `json:"compatibility_text"`
}

func (p *ProfileResponse) ToJSON() ([]byte, error) {
	return json.Marshal(p)
}
