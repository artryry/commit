package recommendations

import (
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"strconv"
	"strings"

	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	profilepb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/profiles/proto/gen"
	"google.golang.org/protobuf/encoding/protojson"
)

type Handler struct {
	profiles *profiles.ProfileClient
}

func NewHandler(p *profiles.ProfileClient) *Handler {
	return &Handler{profiles: p}
}

// GetRecommendations handles GET /api/v1/recommendations?ids=1,2,3&...
// Optional filter query params (same shape as profiles GetProfilesWithFilter) are expected to be
// provided by the caller (e.g. from the recommendations service response), not stored in the gateway.
func (h *Handler) GetRecommendations(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	q := r.URL.Query()
	ids, err := parseCommaSeparatedInt64IDs(q.Get("ids"))
	if err != nil || len(ids) == 0 {
		http.Error(w, "ids query param is required (comma-separated user ids)", http.StatusBadRequest)
		return
	}

	req := &profilepb.GetProfilesWithFilterRequest{
		UserIds: ids,
	}

	if s := strings.TrimSpace(q.Get("relationship_type")); s != "" {
		if rt, ok := parseRelationshipTypePB(s); ok {
			v := rt
			req.RelationshipType = &v
		}
	}
	if v, ok := parseOptionalInt64Query(q, "age_from"); ok {
		req.AgeFrom = v
	}
	if v, ok := parseOptionalInt64Query(q, "age_to"); ok {
		req.AgeTo = v
	}
	if s := strings.TrimSpace(q.Get("city")); s != "" {
		req.City = &s
	}
	if s := strings.TrimSpace(q.Get("sign")); s != "" {
		req.Sign = &s
	}
	if tags := parseCommaSeparatedStrings(q.Get("tags")); len(tags) > 0 {
		req.Tags = tags
	}

	resp, err := h.profiles.GetProfilesWithFilter(r.Context(), req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	out, err := protojson.Marshal(resp)
	if err != nil {
		http.Error(w, "failed to encode response", http.StatusInternalServerError)
		return
	}
	_, _ = w.Write(out)
}

// Filters is markup for /api/v1/recommendations/filters (recommendations service will own filter persistence).
func (h *Handler) Filters(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusNotImplemented)
	_ = json.NewEncoder(w).Encode(map[string]string{
		"error": "recommendations filters are served by the recommendations service (not implemented in gateway)",
	})
}

func parseCommaSeparatedInt64IDs(raw string) ([]int64, error) {
	if strings.TrimSpace(raw) == "" {
		return nil, errors.New("empty ids")
	}
	parts := strings.Split(raw, ",")
	out := make([]int64, 0, len(parts))
	for _, part := range parts {
		id, err := strconv.ParseInt(strings.TrimSpace(part), 10, 64)
		if err != nil {
			return nil, errors.New("invalid id")
		}
		out = append(out, id)
	}
	return out, nil
}

func parseOptionalInt64Query(q url.Values, key string) (*int64, bool) {
	s := strings.TrimSpace(q.Get(key))
	if s == "" {
		return nil, false
	}
	v, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		return nil, false
	}
	return &v, true
}

func parseCommaSeparatedStrings(raw string) []string {
	if strings.TrimSpace(raw) == "" {
		return nil
	}
	parts := strings.Split(raw, ",")
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		if t := strings.TrimSpace(p); t != "" {
			out = append(out, t)
		}
	}
	return out
}

func parseRelationshipTypePB(s string) (profilepb.RelationshipType, bool) {
	s = strings.ToUpper(strings.TrimSpace(s))
	if s == "" {
		return 0, false
	}
	switch s {
	case "FRIENDSHIP", "SEARCH_FOR_FRIENDSHIP":
		return profilepb.RelationshipType_SEARCH_FOR_FRIENDSHIP, true
	case "RELATIONSHIP", "SEARCH_FOR_RELATIONSHIP":
		return profilepb.RelationshipType_SEARCH_FOR_RELATIONSHIP, true
	case "NETWORKING", "SEARCH_FOR_NETWORKING":
		return profilepb.RelationshipType_SEARCH_FOR_NETWORKING, true
	case "UNSPECIFIED", "SEARCH_FOR_UNSPECIFIED":
		return profilepb.RelationshipType_SEARCH_FOR_UNSPECIFIED, true
	default:
		return 0, false
	}
}
