package swipes

import (
	"encoding/json"
	"net/http"

	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	"github.com/artryry/commit/services/api-gateway/src/clients/swipes"
	"github.com/artryry/commit/services/api-gateway/src/internal/common"
	profilepb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/profiles/proto/gen"
	swipespb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/swipes/proto/gen"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type Handler struct {
	swipes   *swipes.Client
	profiles *profiles.ProfileClient
}

func NewHandler(swipesClient *swipes.Client, profilesClient *profiles.ProfileClient) *Handler {
	return &Handler{swipes: swipesClient, profiles: profilesClient}
}

type swipeBody struct {
	TargetUserID int64 `json:"target_user_id"`
	Liked        bool  `json:"liked"`
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

	writeJSON(w, http.StatusOK, resp)
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
