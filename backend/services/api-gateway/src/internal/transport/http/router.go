package router

import (
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/artryry/commit/services/api-gateway/src/clients"
	"github.com/artryry/commit/services/api-gateway/src/internal/config"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/middleware"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/proxy"
)

func NewRouter(clients *clients.Clients, handlers *handlers.Handlers, cfg *config.Config) *chi.Mux {
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
			r.Mount("/auth/delete", proxy.New(cfg.AuthServiceURL))
			r.Mount("/auth/logout", proxy.New(cfg.AuthServiceURL))

			// -------- PROFILE --------
			// r.Route("/profile", func(r chi.Router) {
			// 	r.Get("/me", handlers.Profile.GetMe)
			// 	r.Put("/me", handlers.Profile.UpdateMe)

			// 	r.Get("/{user_id}", handlers.Profile.GetByID)

			// 	r.Post("/images", handlers.Profile.UploadImage)
			// })

			// -------- RECOMMENDATIONS --------
			// r.Route("/recommendations", func(r chi.Router) {
			// 	r.Get("/", handlers.Recommendation.GetFeed)
			// })

			// -------- SWIPES --------
			// r.Route("/swipes", func(r chi.Router) {
			// 	r.Post("/", handlers.Swipe.Action)
			// })

			// -------- MATCHES --------
			// r.Route("/matches", func(r chi.Router) {
			// 	r.Get("/", handlers.Swipe.GetMatches)
			// })

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
