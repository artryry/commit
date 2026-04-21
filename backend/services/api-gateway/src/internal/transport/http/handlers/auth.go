package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/artryry/commit/services/api-gateway/src/clients/auth"
	"github.com/artryry/commit/services/api-gateway/src/internal/common"
	"github.com/artryry/commit/services/api-gateway/src/internal/dto"
)

type authHandlers struct {
}

func newAuthHandlers() *authHandlers {
	return &authHandlers{}
}

func (h *authHandlers) Authorize(c *auth.GRPCClient) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var authReq dto.AuthRequest

		err := common.DecodeJsonBody(r, &authReq)
		if err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if authReq.Password == "" || authReq.Email == "" {
			http.Error(w, "Some required data is missing", http.StatusBadRequest)
			return
		}

		resp, err := c.Authorize(r.Context(), &authReq)
		if err != nil {
			http.Error(w, "Authorization failed", http.StatusUnauthorized)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(&dto.AuthResponse{
			JWT:          resp.JWT,
			RefreshToken: resp.RefreshToken,
		})
	}
}

func (h *authHandlers) Register(c *auth.GRPCClient) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var regReq dto.RegisterRequest

		err := common.DecodeJsonBody(r, &regReq)
		if err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if regReq.Password == "" || regReq.Email == "" {
			http.Error(w, "Some required data is missing", http.StatusBadRequest)
			return
		}

		resp, err := c.Register(r.Context(), &regReq)
		if err != nil {
			http.Error(w, "Registration failed", http.StatusBadRequest)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(&dto.RegisterResponse{
			JWT:          resp.JWT,
			RefreshToken: resp.RefreshToken,
		})
	}
}

func (h *authHandlers) Refresh(c *auth.GRPCClient) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var refreshReq dto.RefreshRequest

		err := common.DecodeJsonBody(r, &refreshReq)
		if err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if refreshReq.RefreshToken == "" {
			http.Error(w, "Refresh token is missing", http.StatusBadRequest)
			return
		}

		jwt, err := c.Refresh(r.Context(), &refreshReq)
		if err != nil {
			http.Error(w, "Refresh failed", http.StatusUnauthorized)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(&dto.RefreshResponse{
			JWT: jwt,
		})
	}
}

func (h *authHandlers) Delete(c *auth.GRPCClient) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var delReq dto.DeleteAccountRequest

		err := common.DecodeJsonBody(r, &delReq)
		if err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if delReq.JWT == "" || delReq.RefreshToken == "" {
			http.Error(w, "Some required data is missing", http.StatusBadRequest)
			return
		}

		success, err := c.Delete(r.Context(), &delReq)
		if err != nil {
			http.Error(w, "Delete failed", http.StatusBadRequest)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(&dto.DeleteAccountResponse{
			Success: success,
		})
	}
}
