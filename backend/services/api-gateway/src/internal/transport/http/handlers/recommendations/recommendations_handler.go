package recommendations

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"strings"

	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	recclient "github.com/artryry/commit/services/api-gateway/src/clients/recommendations"
	"github.com/artryry/commit/services/api-gateway/src/internal/common"
	profilepb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/profiles/proto/gen"
	recommendationpb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/recommendations/proto/gen"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
)

type Handler struct {
	rec      *recclient.RecommendationClient
	profiles *profiles.ProfileClient
}

func NewHandler(rec *recclient.RecommendationClient, profiles *profiles.ProfileClient) *Handler {
	return &Handler{rec: rec, profiles: profiles}
}

// GetRecommendations handles GET /api/v1/recommendations with no query or body.
// It calls the recommendations service for candidate ids + filter, then profiles GetProfilesWithFilter.
func (h *Handler) GetRecommendations(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	userID, ok := userIDFromRequest(r)
	if !ok {
		writeJSONError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	recResp, err := h.rec.GetRecommendationsForUser(r.Context(), &recommendationpb.GetRecommendationsForUserRequest{
		UserId: userID,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}

	profReq := profileFilterFromRecommendations(recResp)
	profResp, err := h.profiles.GetProfilesWithFilter(r.Context(), profReq)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}

	out, err := protojson.Marshal(profResp)
	if err != nil {
		http.Error(w, "failed to encode response", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(out)
}

// Filters handles GET/POST /api/v1/recommendations/filters via the recommendations service.
func (h *Handler) Filters(w http.ResponseWriter, r *http.Request) {
	userID, ok := userIDFromRequest(r)
	if !ok {
		writeJSONError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	switch r.Method {
	case http.MethodGet:
		resp, err := h.rec.GetFilters(r.Context(), &recommendationpb.GetFiltersRequest{UserId: userID})
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		writeProtoJSON(w, http.StatusOK, resp)
	case http.MethodPost:
		var body filtersHTTPBody
		if err := common.DecodeJsonBody(r, &body); err != nil {
			writeJSONError(w, http.StatusBadRequest, "invalid json body")
			return
		}
		req := &recommendationpb.SetFiltersRequest{UserId: userID}
		if body.RelationshipType != nil {
			rt, err := parseRelationshipTypeString(*body.RelationshipType)
			if err != nil {
				writeJSONError(w, http.StatusBadRequest, err.Error())
				return
			}
			v := rt
			req.RelationshipType = &v
		}
		if body.AgeFrom != nil {
			req.AgeFrom = body.AgeFrom
		}
		if body.AgeTo != nil {
			req.AgeTo = body.AgeTo
		}
		if body.City != nil {
			req.City = body.City
		}
		if body.Sign != nil {
			req.Sign = body.Sign
		}
		if body.Tags != nil {
			req.Tags = body.Tags
		}
		resp, err := h.rec.SetFilters(r.Context(), req)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		writeProtoJSON(w, http.StatusOK, resp)
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

type filtersHTTPBody struct {
	RelationshipType *string  `json:"relationship_type"`
	AgeFrom          *int64   `json:"age_from"`
	AgeTo            *int64   `json:"age_to"`
	City             *string  `json:"city"`
	Sign             *string  `json:"sign"`
	Tags             []string `json:"tags"`
}

func profileFilterFromRecommendations(rec *recommendationpb.GetRecommendationsForUserResponse) *profilepb.GetProfilesWithFilterRequest {
	req := &profilepb.GetProfilesWithFilterRequest{
		UserIds: rec.GetCandidateUserIds(),
	}
	if len(rec.Tags) > 0 {
		req.Tags = rec.Tags
	}
	if rec.RelationshipType != nil {
		v := *rec.RelationshipType
		req.RelationshipType = &v
	}
	if rec.AgeFrom != nil {
		req.AgeFrom = rec.AgeFrom
	}
	if rec.AgeTo != nil {
		req.AgeTo = rec.AgeTo
	}
	if rec.City != nil {
		req.City = rec.City
	}
	if rec.Sign != nil {
		req.Sign = rec.Sign
	}
	return req
}

func userIDFromRequest(r *http.Request) (int64, bool) {
	v := r.Context().Value(common.UserIDKey)
	switch val := v.(type) {
	case int:
		return int64(val), true
	case int64:
		return val, true
	case float64:
		return int64(val), true
	case string:
		id, err := strconv.ParseInt(val, 10, 64)
		if err != nil {
			return 0, false
		}
		return id, true
	default:
		return 0, false
	}
}

func parseRelationshipTypeString(value string) (profilepb.RelationshipType, error) {
	switch strings.ToUpper(strings.TrimSpace(value)) {
	case "FRIENDSHIP", "SEARCH_FOR_FRIENDSHIP":
		return profilepb.RelationshipType_SEARCH_FOR_FRIENDSHIP, nil
	case "RELATIONSHIP", "SEARCH_FOR_RELATIONSHIP":
		return profilepb.RelationshipType_SEARCH_FOR_RELATIONSHIP, nil
	case "NETWORKING", "SEARCH_FOR_NETWORKING":
		return profilepb.RelationshipType_SEARCH_FOR_NETWORKING, nil
	case "", "UNSPECIFIED", "SEARCH_FOR_UNSPECIFIED":
		return profilepb.RelationshipType_SEARCH_FOR_UNSPECIFIED, nil
	default:
		return 0, errors.New("invalid relationship_type")
	}
}

func writeJSONError(w http.ResponseWriter, status int, msg string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]string{"error": msg})
}

func writeProtoJSON(w http.ResponseWriter, status int, m proto.Message) {
	out, err := protojson.Marshal(m)
	if err != nil {
		http.Error(w, "failed to encode response", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_, _ = w.Write(out)
}
