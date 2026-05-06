package handlers

import (
	"net/http"

	"github.com/artryry/commit/services/api-gateway/src/clients"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers/profiles"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers/recommendations"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers/swipes"
)

type Handlers struct {
	Profiles        ProfileHandler
	Recommendations RecommendationsHandler
	Swipes          SwipesHandler
}

func NewHandlers(c *clients.Clients) *Handlers {
	return &Handlers{
		Profiles:        profiles.NewProfileHandler(c.Profiles),
		Recommendations: recommendations.NewHandler(c.Recommendations, c.Profiles),
		Swipes:          swipes.NewHandler(),
	}
}

type ProfileHandler interface {
	GetMe(w http.ResponseWriter, r *http.Request)
	UpdateMe(w http.ResponseWriter, r *http.Request)
	GetByIDs(w http.ResponseWriter, r *http.Request)
	GetByID(w http.ResponseWriter, r *http.Request)
	UploadImages(w http.ResponseWriter, r *http.Request)
	DeleteImages(w http.ResponseWriter, r *http.Request)
	AttachTags(w http.ResponseWriter, r *http.Request)
	DetachTags(w http.ResponseWriter, r *http.Request)
}

type RecommendationsHandler interface {
	GetRecommendations(w http.ResponseWriter, r *http.Request)
	Filters(w http.ResponseWriter, r *http.Request)
}

type SwipesHandler interface {
	Action(w http.ResponseWriter, r *http.Request)
	GetMatches(w http.ResponseWriter, r *http.Request)
}
