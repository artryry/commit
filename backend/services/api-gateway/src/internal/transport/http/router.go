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

		// ================= AUTH =================
		// r.Route("/auth", func(r chi.Router) {
		// 	r.Post("/register", handlers.Auth.Register(clients.Auth))
		// 	r.Post("/login", handlers.Auth.Authorize(clients.Auth))
		// 	r.Post("/refresh", handlers.Auth.Refresh(clients.Auth))
		// })
		r.Route("/auth", func(r chi.Router) {
			r.Mount("/register", proxy.New(cfg.AuthServiceURL))
			r.Mount("/login", proxy.New(cfg.AuthServiceURL))
			r.Mount("/token", proxy.New(cfg.AuthServiceURL))
		})

		// ================= PROTECTED ROUTES =================
		r.Group(func(r chi.Router) {
			r.Use(middleware.JWT(clients.Auth, cfg.JWTPublicKey))

			// -------- AUTH --------
			r.Route("/auth", func(r chi.Router) {
				r.Mount("/delete", proxy.New(cfg.AuthServiceURL))
				r.Mount("/logout", proxy.New(cfg.AuthServiceURL))
			})

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
