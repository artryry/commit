package app

import (
	"log"
	"net/http"

	"github.com/artryry/commit/services/api-gateway/src/clients"
	"github.com/artryry/commit/services/api-gateway/src/internal/common"
	"github.com/artryry/commit/services/api-gateway/src/internal/config"
	router "github.com/artryry/commit/services/api-gateway/src/internal/transport/http"
	"github.com/artryry/commit/services/api-gateway/src/internal/transport/http/handlers"

	"github.com/go-chi/chi/v5"
)

type App struct {
	Router  *chi.Mux
	Clients *clients.Clients
	Keys    *common.Keys
}

func NewApp() *App {
	clients := clients.NewClients()
	handlers := handlers.NewHandlers()
	cfg := config.Load()
	keys := common.NewKeys(clients.Auth)

	return &App{
		Router:  router.NewRouter(clients, handlers, cfg),
		Clients: clients,
		Keys:    keys,
	}
}

func (a *App) Run() {
	log.Println("Server is starting...")
	log.Fatal(http.ListenAndServe(common.Address, a.Router))
	log.Printf("Server is running on %s%s", common.Address, common.Port)
}
