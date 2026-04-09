package handlers

import "net/http"

type authHandlers struct {
}

func newAuthHandlers() *authHandlers {
	return &authHandlers{}
}

func (h *authHandlers) Authorize(w http.ResponseWriter, r *http.Request) {}

func (h *authHandlers) Register(w http.ResponseWriter, r *http.Request) {}

func (h *authHandlers) Refresh(w http.ResponseWriter, r *http.Request) {}

func (h *authHandlers) Delete(w http.ResponseWriter, r *http.Request) {}
