package main

import (
	"fmt"
	"os"

	"github.com/artryry/commit/backend/services/swipes/src/internal/config"
	"github.com/artryry/commit/backend/services/swipes/src/internal/database"
	kafkaProducer "github.com/artryry/commit/backend/services/swipes/src/internal/kafka"
	"github.com/artryry/commit/backend/services/swipes/src/internal/logger"
	"github.com/artryry/commit/backend/services/swipes/src/internal/repository"
	"github.com/artryry/commit/backend/services/swipes/src/internal/service"
	grpcserver "github.com/artryry/commit/backend/services/swipes/src/internal/transport/grpc"
	"github.com/artryry/commit/backend/services/swipes/src/internal/transport/grpc/handlers"
)

func main() {
	logger.Init()
	cfg := config.Load()

	db, err := database.NewPostgres(cfg)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	if err := database.RunMigrations(cfg); err != nil {
		panic(err)
	}

	pub, err := kafkaProducer.NewProducer(cfg.Kafka)
	if err != nil {
		panic(err)
	}
	defer pub.Close()

	repo := repository.New(db)
	svc := service.New(repo, pub)
	h := handlers.New(svc)

	addr := fmt.Sprintf(":%s", cfg.GRPC.Port)
	logger.Info("swipes grpc listening", "addr", addr)

	if err := grpcserver.Run(addr, h); err != nil {
		logger.Error("grpc stopped", "err", err)
		os.Exit(1)
	}
}
