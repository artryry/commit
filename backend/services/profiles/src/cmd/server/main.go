package main

import (
	"github.com/artryry/commit/services/profiles/src/internal/config"
	"github.com/artryry/commit/services/profiles/src/internal/database"
	"github.com/artryry/commit/services/profiles/src/internal/logger"
	"github.com/artryry/commit/services/profiles/src/internal/repositories/postgres"
	grpcTransport "github.com/artryry/commit/services/profiles/src/internal/transport/grpc"
	"github.com/artryry/commit/services/profiles/src/internal/transport/grpc/handlers"
)

func main() {
	cfg := config.Load()

	logger.Init(cfg.App.Port)

	db, err := database.NewPostgres(cfg)
	if err != nil {
		logger.Error("failed to connect to postgres", err)
		panic(err)
	}

	defer db.Close()

	err = database.RunMigrations(cfg)

	if err != nil {
		logger.Error(
			"failed to run migrations",
			"error", err,
		)
		panic(err)
	}

	repo := postgres.NewProfileRepository(cfg, db)

	profileService := service.NewProfileService(repo)

	handler := handlers.NewProfileHandler(profileService)

	if err := grpcTransport.Run(handler); err != nil {
		logger.Error("failed to run grpc server", err)
	}

	logger.Info("service started")
}
