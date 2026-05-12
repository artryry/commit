package swipes

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	"github.com/artryry/commit/services/api-gateway/src/clients/swipes"
	"github.com/artryry/commit/services/api-gateway/src/internal/common"
	profilepb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/profiles/proto/gen"
	swipespb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/swipes/proto/gen"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/encoding/protojson"
)

type Handler struct {
	swipes   *swipes.Client
	profiles *profiles.ProfileClient
}

func NewHandler(swipesClient *swipes.Client, profilesClient *profiles.ProfileClient) *Handler {
	return &Handler{swipes: swipesClient, profiles: profilesClient}
}

type swipeBody struct {
	TargetUserID int64
	Liked          bool
}

// UnmarshalJSON accepts strict JSON and common client quirks (string ids, string booleans).
func (b *swipeBody) UnmarshalJSON(data []byte) error {
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	tid, ok := raw["target_user_id"]
	if !ok {
		return fmt.Errorf("missing target_user_id")
	}
	var n float64
	if err := json.Unmarshal(tid, &n); err == nil {
		b.TargetUserID = int64(n)
	} else {
		var s string
		if err := json.Unmarshal(tid, &s); err != nil {
			return err
		}
		id, err := strconv.ParseInt(strings.TrimSpace(s), 10, 64)
		if err != nil {
			return err
		}
		b.TargetUserID = id
	}
	lk, ok := raw["liked"]
	if !ok {
		return fmt.Errorf("missing liked")
	}
	if err := json.Unmarshal(lk, &b.Liked); err == nil {
		return nil
	}
	var s string
	if err := json.Unmarshal(lk, &s); err != nil {
		return err
	}
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "true", "1", "yes":
		b.Liked = true
	case "false", "0", "no":
		b.Liked = false
	default:
		return fmt.Errorf("invalid liked")
	}
	return nil
}

// ListIncomingLikes handles GET /api/v1/swipes: incoming-like user ids from swipes gRPC, then profiles GetProfiles
// (same aggregation pattern as GET /api/v1/recommendations).
func (h *Handler) ListIncomingLikes(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	likes, err := h.swipes.ListIncomingLikes(r.Context(), &swipespb.ListIncomingLikesRequest{UserId: userID})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	ids := likes.GetUserIds()
	var profResp *profilepb.GetProfilesResponse
	if len(ids) == 0 {
		profResp = &profilepb.GetProfilesResponse{}
	} else {
		profResp, err = h.profiles.GetProfiles(r.Context(), &profilepb.GetProfilesRequest{UserIds: ids})
		if err != nil {
			writeError(w, http.StatusBadGateway, err.Error())
			return
		}
	}

	out, err := protojson.Marshal(profResp)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to encode response")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(out)
}

func (h *Handler) Action(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	var body swipeBody
	if err := common.DecodeJsonBody(r, &body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid json body")
		return
	}
	if body.TargetUserID == 0 {
		writeError(w, http.StatusBadRequest, "target_user_id is required")
		return
	}

	resp, err := h.swipes.RecordSwipe(r.Context(), &swipespb.RecordSwipeRequest{
		ViewerUserId: userID,
		TargetUserId: body.TargetUserID,
		Liked:        body.Liked,
	})
	if err != nil {
		if st, ok := status.FromError(err); ok && st.Code() == codes.InvalidArgument {
			writeError(w, http.StatusBadRequest, st.Message())
			return
		}
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, map[string]bool{"success": resp.GetSuccess()})
}

func (h *Handler) GetMatches(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	sm, err := h.swipes.ListMatches(r.Context(), &swipespb.ListMatchesRequest{UserId: userID})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	ids := sm.GetMatchedUserIds()
	if len(ids) == 0 {
		writeJSON(w, http.StatusOK, map[string]any{"profiles_data": []any{}})
		return
	}

	profResp, err := h.profiles.GetProfiles(r.Context(), &profilepb.GetProfilesRequest{UserIds: ids})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, profResp)
}

func getUserID(r *http.Request) (int64, bool) {
	v := r.Context().Value(common.UserIDKey)
	switch val := v.(type) {
	case int:
		return int64(val), true
	case int64:
		return val, true
	case float64:
		return int64(val), true
	default:
		return 0, false
	}
}

func writeJSON(w http.ResponseWriter, statusCode int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, statusCode int, message string) {
	writeJSON(w, statusCode, map[string]string{"error": message})
}
