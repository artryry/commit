package profiles

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"strconv"
	"strings"

	"github.com/artryry/commit/services/api-gateway/src/clients/profiles"
	"github.com/artryry/commit/services/api-gateway/src/internal/common"
	profilepb "github.com/artryry/commit/services/api-gateway/src/internal/transport/grpc/profiles/proto/gen"
	"github.com/go-chi/chi/v5"
)

type ProfileHandler struct {
	client *profiles.ProfileClient
}

func NewProfileHandler(client *profiles.ProfileClient) *ProfileHandler {
	return &ProfileHandler{client: client}
}

func (h *ProfileHandler) GetMe(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	resp, err := h.client.GetProfile(r.Context(), &profilepb.GetProfileRequest{UserId: userID})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func (h *ProfileHandler) UpdateMe(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	var reqBody updateProfileRequest
	if err := common.DecodeJsonBody(r, &reqBody); err != nil {
		writeError(w, http.StatusBadRequest, "invalid json body")
		return
	}

	pbReq := &profilepb.UpdateProfileRequest{
		UserId: userID,
	}
	if reqBody.Username != nil {
		pbReq.Username = reqBody.Username
	}
	if reqBody.AvatarImageID != nil {
		pbReq.AvatarImageId = reqBody.AvatarImageID
	}
	if reqBody.Bio != nil {
		pbReq.Bio = reqBody.Bio
	}
	if reqBody.City != nil {
		pbReq.City = reqBody.City
	}
	if reqBody.SearchFor != nil {
		pbReq.SearchFor = reqBody.SearchFor
	}
	if reqBody.RelationshipType != nil {
		enumValue, err := parseRelationshipType(*reqBody.RelationshipType)
		if err != nil {
			writeError(w, http.StatusBadRequest, err.Error())
			return
		}
		pbReq.RelationshipType = &enumValue
	}

	resp, err := h.client.UpdateProfile(r.Context(), pbReq)
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func (h *ProfileHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	idRaw := chi.URLParam(r, "user_id")
	userID, err := strconv.ParseInt(idRaw, 10, 64)
	if err != nil {
		writeError(w, http.StatusBadRequest, "invalid user_id")
		return
	}

	resp, err := h.client.GetProfile(r.Context(), &profilepb.GetProfileRequest{UserId: userID})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func (h *ProfileHandler) GetByIDs(w http.ResponseWriter, r *http.Request) {
	ids, err := parseIDsQuery(r.URL.Query().Get("ids"))
	if err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	resp, err := h.client.GetProfiles(r.Context(), &profilepb.GetProfilesRequest{UserIds: ids})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func (h *ProfileHandler) UploadImages(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	if err := r.ParseMultipartForm(20 << 20); err != nil {
		writeError(w, http.StatusBadRequest, "failed to parse multipart form")
		return
	}

	files := r.MultipartForm.File["images"]
	if len(files) == 0 {
		files = r.MultipartForm.File["image"]
	}
	if len(files) == 0 {
		writeError(w, http.StatusBadRequest, "no image files provided")
		return
	}

	uploaded := make([]*profilepb.Image, 0, len(files))
	for _, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			writeError(w, http.StatusBadRequest, "failed to open uploaded file")
			return
		}

		data, readErr := io.ReadAll(file)
		_ = file.Close()
		if readErr != nil {
			writeError(w, http.StatusBadRequest, "failed to read uploaded file")
			return
		}

		resp, err := h.client.UploadProfileImage(r.Context(), &profilepb.UploadProfileImageRequest{
			UserId: userID,
			Image:  data,
		})
		if err != nil {
			writeError(w, http.StatusBadGateway, err.Error())
			return
		}

		uploaded = append(uploaded, resp.GetImage())
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"user_id": userID,
		"images":  uploaded,
	})
}

func (h *ProfileHandler) DeleteImages(w http.ResponseWriter, r *http.Request) {
	var reqBody imageIDsRequest
	if err := common.DecodeJsonBody(r, &reqBody); err != nil {
		writeError(w, http.StatusBadRequest, "invalid json body")
		return
	}
	if len(reqBody.ImageIDs) == 0 {
		writeError(w, http.StatusBadRequest, "image_ids must not be empty")
		return
	}

	resp, err := h.client.DeleteProfileImages(r.Context(), &profilepb.DeleteProfileImagesRequest{
		ImageIds: reqBody.ImageIDs,
	})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func (h *ProfileHandler) AttachTags(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	var reqBody tagsRequest
	if err := common.DecodeJsonBody(r, &reqBody); err != nil {
		writeError(w, http.StatusBadRequest, "invalid json body")
		return
	}

	resp, err := h.client.AttachProfileTags(r.Context(), &profilepb.AddProfileTagsRequest{
		UserId: userID,
		Tags:   reqBody.Tags,
	})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

func (h *ProfileHandler) DetachTags(w http.ResponseWriter, r *http.Request) {
	userID, ok := getUserID(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "missing user id in token")
		return
	}

	var reqBody tagsRequest
	if err := common.DecodeJsonBody(r, &reqBody); err != nil {
		writeError(w, http.StatusBadRequest, "invalid json body")
		return
	}

	resp, err := h.client.DetachProfileTags(r.Context(), &profilepb.DetachProfileTagsRequest{
		UserId: userID,
		Tags:   reqBody.Tags,
	})
	if err != nil {
		writeError(w, http.StatusBadGateway, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, resp)
}

type updateProfileRequest struct {
	Username         *string `json:"username"`
	AvatarImageID    *int64  `json:"avatar_image_id"`
	Bio              *string `json:"bio"`
	City             *string `json:"city"`
	SearchFor        *string `json:"search_for"`
	RelationshipType *string `json:"relationship_type"`
}

type imageIDsRequest struct {
	ImageIDs []int64 `json:"image_ids"`
}

type tagsRequest struct {
	Tags []string `json:"tags"`
}

func parseIDsQuery(raw string) ([]int64, error) {
	if strings.TrimSpace(raw) == "" {
		return nil, errors.New("ids query param is required")
	}

	parts := strings.Split(raw, ",")
	result := make([]int64, 0, len(parts))
	for _, part := range parts {
		id, err := strconv.ParseInt(strings.TrimSpace(part), 10, 64)
		if err != nil {
			return nil, errors.New("ids must be comma-separated int64 values")
		}
		result = append(result, id)
	}

	return result, nil
}

func parseRelationshipType(value string) (profilepb.RelationshipType, error) {
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

func getUserID(r *http.Request) (int64, bool) {
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

func writeJSON(w http.ResponseWriter, statusCode int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, statusCode int, message string) {
	writeJSON(w, statusCode, map[string]string{"error": message})
}
