package router

import (
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/middleware"
)

func NewRouter() *chi.Mux {
	router := chi.NewRouter()

	// Global Middleware
	router.Use(middleware.LoggingMiddleware)

	// Protected Routes
	router.Group(func(r chi.Router) {
		r.Use(middleware.JWT)

		r.Get("/feed", func(w http.ResponseWriter, r *http.Request) {})
	})

	// Public Routes
	router.Route("/auth", func(r chi.Router) {})

	return router
}
