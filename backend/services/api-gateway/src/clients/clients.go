package clients

import (
	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	"github.com/artryry/commit/services/api-gateway/src/clients/recommendations"
	"github.com/artryry/commit/services/api-gateway/src/clients/swipes"
)

type Clients struct {
	Profiles        *profiles.ProfileClient
	Recommendations *recommendations.RecommendationClient
	Swipes          *swipes.Client
}

func NewClients(profileGRPCAddr, recommendationsGRPCAddr, swipesGRPCAddr string) (*Clients, error) {
	profileClient, err := profiles.NewProfileClient(profileGRPCAddr)
	if err != nil {
		return nil, err
	}

	recClient, err := recommendations.NewRecommendationClient(recommendationsGRPCAddr)
	if err != nil {
		_ = profileClient.Close()
		return nil, err
	}

	swipesClient, err := swipes.New(swipesGRPCAddr)
	if err != nil {
		_ = profileClient.Close()
		_ = recClient.Close()
		return nil, err
	}

	return &Clients{
		Profiles:        profileClient,
		Recommendations: recClient,
		Swipes:          swipesClient,
	}, nil
}
