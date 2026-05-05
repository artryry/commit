package app

import (
	"fmt"
	"log"
	"net/http"

	"github.com/artryry/commit/services/api-gateway/src/clients"
	"github.com/artryry/commit/services/api-gateway/src/internal/config"
	router "github.com/artryry/commit/services/api-gateway/src/internal/transport/http"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers"

	"github.com/go-chi/chi/v5"
)

type App struct {
	Router  *chi.Mux
	Clients *clients.Clients
	cfg     *config.Config
	// Keys    *common.Keys
}

func NewApp() *App {
	cfg := config.Load()
	clients, err := clients.NewClients(cfg.ProfileServiceGRPC)
	if err != nil {
		log.Fatal(err)
	}
	handlers := handlers.NewHandlers(clients)
	// keys := common.NewKeys(cfg, clients.Auth)

	return &App{
		Router:  router.NewRouter(handlers, cfg),
		Clients: clients,
		cfg:     cfg,
		// Keys:    keys,
	}
}

func (a *App) Run() {
	log.Println("Server is started")
	log.Fatal(http.ListenAndServe(fmt.Sprintf("%s:%s", a.cfg.Address, a.cfg.Port), a.Router))
	log.Printf("Server is stopped")
}
