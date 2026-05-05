package router

import (
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/artryry/commit/services/api-gateway/src/internal/config"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/middleware"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/proxy"
)

func NewRouter(handlers *handlers.Handlers, cfg *config.Config) *chi.Mux {
	router := chi.NewRouter()

	// Global Middleware
	router.Use(middleware.LoggingMiddleware)

	// Health check
	router.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})

	// API V1
	router.Route("/api/v1", func(r chi.Router) {

		// ================= AUTH (Public Endpoints) =================
		r.Mount("/auth/register", proxy.New(cfg.AuthServiceURL))
		r.Mount("/auth/login", proxy.New(cfg.AuthServiceURL))
		r.Mount("/auth/token", proxy.New(cfg.AuthServiceURL))

		// ================= PROTECTED ROUTES =================
		r.Group(func(r chi.Router) {
			r.Use(middleware.JWT(cfg.JWTPublicKey))

			// -------- AUTH (Protected Endpoints) --------
			r.Mount("/auth/me", proxy.New(cfg.AuthServiceURL))
			r.Mount("/auth/logout", proxy.New(cfg.AuthServiceURL))

			// -------- PROFILE --------
			r.Route("/profiles", func(r chi.Router) {
				r.Get("/me", handlers.Profiles.GetMe)
				r.Put("/me", handlers.Profiles.UpdateMe)

				r.Get("/", handlers.Profiles.GetByIDs)
				r.Get("/{user_id}", handlers.Profiles.GetByID)

				r.Post("/images", handlers.Profiles.UploadImages)
				r.Delete("/images", handlers.Profiles.DeleteImages)

				r.Post("/tags", handlers.Profiles.AttachTags)
				r.Delete("/tags", handlers.Profiles.DetachTags)
			})

			// -------- RECOMMENDATIONS --------
			r.Route("/recommendations", func(r chi.Router) {
				r.Get("/", handlers.Recommendations.GetRecommendations)
				r.Get("/filters", handlers.Recommendations.Filters)
			})

			// -------- SWIPES --------
			r.Route("/swipes", func(r chi.Router) {
				r.Post("/", handlers.Swipes.Action)
			})

			// -------- MATCHES --------
			r.Route("/matches", func(r chi.Router) {
				r.Get("/", handlers.Swipes.GetMatches)
			})

			// -------- CHATS --------
			// r.Route("/chats", func(r chi.Router) {
			// 	r.Get("/", handlers.Chat.GetChats)
			// 	r.Get("/{chat_id}/messages", handlers.Chat.GetMessages)
			// })

			// -------- NOTIFICATIONS --------
			// r.Route("/notifications", func(r chi.Router) {
			// 	r.Get("/", handlers.Notification.GetAll)
			// })
		})
	})

	return router
}
