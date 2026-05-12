package recommendations

import (
	"bytes"
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
// It calls the recommendations service for candidate ids, then profiles GetProfiles to load rows.
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

	profResp, err := h.profiles.GetProfiles(r.Context(), &profilepb.GetProfilesRequest{
		UserIds: recResp.GetCandidateUserIds(),
	})
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

type compatibilityHTTPBody struct {
	UserIDs []int64 `json:"user_ids"`
}

// Compatibility handles POST /api/v1/recommendations/compatibility (body: { "user_ids": [...] }).
func (h *Handler) Compatibility(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	userID, ok := userIDFromRequest(r)
	if !ok {
		writeJSONError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	var body compatibilityHTTPBody
	if err := common.DecodeJsonBody(r, &body); err != nil {
		writeJSONError(w, http.StatusBadRequest, "invalid json body")
		return
	}

	recResp, err := h.rec.GetCompatibilityTexts(r.Context(), &recommendationpb.GetCompatibilityTextsRequest{
		ViewerUserId:   userID,
		OtherUserIds:   body.UserIDs,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}

	writeProtoJSON(w, http.StatusOK, recResp)
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
		// Omit optional proto fields for empty / sentinel JSON so the service clears the filter (NULL), not a restrictive value.
		if body.RelationshipType != nil {
			s := strings.TrimSpace(*body.RelationshipType)
			if s != "" {
				rt, err := parseRelationshipTypeString(s)
				if err != nil {
					writeJSONError(w, http.StatusBadRequest, err.Error())
					return
				}
				if rt != profilepb.RelationshipType_SEARCH_FOR_UNSPECIFIED {
					v := rt
					req.RelationshipType = &v
				}
			}
		}
		if body.AgeFrom != nil && *body.AgeFrom != 0 {
			v := *body.AgeFrom
			req.AgeFrom = &v
		}
		if body.AgeTo != nil && *body.AgeTo != 0 {
			v := *body.AgeTo
			req.AgeTo = &v
		}
		if body.City != nil {
			if s := strings.TrimSpace(*body.City); s != "" {
				req.City = &s
			}
		}
		if body.Sign != nil {
			if s := strings.TrimSpace(*body.Sign); s != "" {
				req.Sign = &s
			}
		}
		if body.Tags != nil {
			cleaned := make([]string, 0, len(body.Tags))
			for _, t := range body.Tags {
				if s := strings.TrimSpace(t); s != "" {
					cleaned = append(cleaned, s)
				}
			}
			req.Tags = cleaned
		}
		if body.PartnerGender != nil {
			s := strings.TrimSpace(*body.PartnerGender)
			if s != "" {
				g, err := parseGenderString(s)
				if err != nil {
					writeJSONError(w, http.StatusBadRequest, err.Error())
					return
				}
				v := g
				req.PartnerGender = &v
			}
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
	RelationshipType *string
	AgeFrom          *int64
	AgeTo            *int64
	City             *string
	Sign             *string
	Tags             []string
	PartnerGender    *string
}

// UnmarshalJSON accepts snake_case (REST docs) and camelCase (matches protobuf JSON from GET /filters).
// Age fields may be JSON numbers or quoted numeric strings (e.g. "100").
func (b *filtersHTTPBody) UnmarshalJSON(data []byte) error {
	*b = filtersHTTPBody{}
	data = bytes.TrimSpace(data)
	if len(data) == 0 || string(data) == "null" {
		return errors.New("empty json body")
	}
	var m map[string]json.RawMessage
	if err := json.Unmarshal(data, &m); err != nil {
		return err
	}
	var err error
	if b.RelationshipType, err = decodeJSONStringPtr(firstRaw(m, "relationship_type", "relationshipType")); err != nil {
		return err
	}
	if b.AgeFrom, err = decodeJSONInt64Ptr(firstRaw(m, "age_from", "ageFrom")); err != nil {
		return err
	}
	if b.AgeTo, err = decodeJSONInt64Ptr(firstRaw(m, "age_to", "ageTo")); err != nil {
		return err
	}
	if b.City, err = decodeJSONStringPtr(firstRaw(m, "city")); err != nil {
		return err
	}
	if b.Sign, err = decodeJSONStringPtr(firstRaw(m, "sign")); err != nil {
		return err
	}
	if b.PartnerGender, err = decodeJSONStringPtr(firstRaw(m, "partner_gender", "partnerGender")); err != nil {
		return err
	}
	if raw, ok := m["tags"]; ok {
		if string(raw) == "null" {
			b.Tags = nil
		} else if err := json.Unmarshal(raw, &b.Tags); err != nil {
			return err
		}
	}
	return nil
}

func firstRaw(m map[string]json.RawMessage, keys ...string) json.RawMessage {
	for _, k := range keys {
		raw, ok := m[k]
		if !ok || string(raw) == "null" {
			continue
		}
		return raw
	}
	return nil
}

func decodeJSONStringPtr(raw json.RawMessage) (*string, error) {
	if len(raw) == 0 {
		return nil, nil
	}
	var s string
	if err := json.Unmarshal(raw, &s); err != nil {
		return nil, err
	}
	return &s, nil
}

func decodeJSONInt64Ptr(raw json.RawMessage) (*int64, error) {
	if len(raw) == 0 {
		return nil, nil
	}
	var n int64
	if err := json.Unmarshal(raw, &n); err == nil {
		return &n, nil
	}
	var f float64
	if err := json.Unmarshal(raw, &f); err == nil {
		v := int64(f)
		return &v, nil
	}
	var s string
	if err := json.Unmarshal(raw, &s); err != nil {
		return nil, errors.New("invalid age value (expected number or numeric string)")
	}
	s = strings.TrimSpace(s)
	if s == "" {
		return nil, nil
	}
	v, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		return nil, errors.New("invalid age value (expected number or numeric string)")
	}
	return &v, nil
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

func parseGenderString(value string) (profilepb.Gender, error) {
	switch strings.ToUpper(strings.TrimSpace(value)) {
	case "MALE", "M":
		return profilepb.Gender_MALE, nil
	case "FEMALE", "F":
		return profilepb.Gender_FEMALE, nil
	default:
		return 0, errors.New("invalid partner_gender (use MALE or FEMALE)")
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
