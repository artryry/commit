package clients

import (
	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	"github.com/artryry/commit/services/api-gateway/src/clients/recommendations"
)

type Clients struct {
	Profiles        *profiles.ProfileClient
	Recommendations *recommendations.RecommendationClient
}

func NewClients(profileGRPCAddr, recommendationsGRPCAddr string) (*Clients, error) {
	profileClient, err := profiles.NewProfileClient(profileGRPCAddr)
	if err != nil {
		return nil, err
	}

	recClient, err := recommendations.NewRecommendationClient(recommendationsGRPCAddr)
	if err != nil {
		_ = profileClient.Close()
		return nil, err
	}

	return &Clients{
		Profiles:        profileClient,
		Recommendations: recClient,
	}, nil
}
