package app

import (
	"fmt"
	"net/http"

	service "github.com/artryry/commit/services/api-gateway/src/internal/core/feed"
)

type App struct {
	feedService service.FeedService
	HTTPHandler http.Handler
}

func NewApp() *App {
	return &App{}
}

func (a *App) Run() {
	fmt.Println("App is running")
}
