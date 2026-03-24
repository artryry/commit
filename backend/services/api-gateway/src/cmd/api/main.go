package main

import "github.com/Ryryr0/commit/api-gateway/internal/app"

func main() {
	app := app.NewApp()
	app.Run()
}
