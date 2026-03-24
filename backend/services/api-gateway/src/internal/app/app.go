package app

import (
	"fmt"
	"net/http"

	service "github.com/Ryryr0/commit/api-gateway/internal/core/feed"
)

type App struct {
	feedService service.FeedService
	HTTPHandler http.Handler
}

func NewApp() *App {
	return &App{
		feedService: service.NewFeedService()
	}
}

func (a *App) Run() {
	fmt.Println("App is running")
}
