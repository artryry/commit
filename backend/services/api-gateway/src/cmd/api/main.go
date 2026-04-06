package main

import "github.com/artryry/commit/services/api-gateway/src/internal/app"

func main() {
	app := app.NewApp()
	app.Run()
}
