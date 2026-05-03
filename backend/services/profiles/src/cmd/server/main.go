package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/artryry/commit/backend/services/profiles/src/internal/config"
	"github.com/artryry/commit/backend/services/profiles/src/internal/database"
	"github.com/artryry/commit/backend/services/profiles/src/internal/logger"
	"github.com/artryry/commit/backend/services/profiles/src/internal/messaging/kafka"
	"github.com/artryry/commit/backend/services/profiles/src/internal/repositories/postgres"
	"github.com/artryry/commit/backend/services/profiles/src/internal/services"
	storage "github.com/artryry/commit/backend/services/profiles/src/internal/storage/s3"
	grpcTransport "github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc"
	"github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc/handlers"
)

func main() {
	cfg := config.Load()

	logger.Init(cfg.App.Port)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	db, err := database.NewPostgres(cfg)
	if err != nil {
		logger.Error("failed to connect to postgres", "err", err)
		panic(err)
	}

	defer db.Close()

	err = database.RunMigrations(cfg)
	if err != nil {
		logger.Error("failed to run migrations", "err", err)
		panic(err)
	}

	profileRepository := postgres.NewProfileRepository(cfg, db)
	imageRepository := postgres.NewImageRepository(db)
	tagRepository := postgres.NewTagRepository(db)

	imageStorage, err := storage.NewImageStorage(cfg)
	if err != nil {
		logger.Error("failed to connect to image storage", "err", err)
		panic(err)
	}

	imageService := services.NewImageService(imageRepository, imageStorage)
	tagService := services.NewTagService(tagRepository)
	profileService := services.NewProfileService(profileRepository)

	kafkaProducer, err := kafka.NewProducer(cfg.Kafka)
	if err != nil {
		logger.Error("failed to init kafka producer", "err", err)
		panic(err)
	}
	defer kafkaProducer.Close()

	handler := handlers.NewProfileHandler(profileService, imageService, tagService, kafkaProducer)

	consumer := kafka.NewUserEventsConsumer(cfg, profileService)
	go func() {
		if err := consumer.Run(ctx); err != nil && !errors.Is(err, context.Canceled) {
			logger.Error("kafka consumer stopped", "err", err)
			panic(err)
		}
	}()

	addr := fmt.Sprintf(":%s", cfg.GRPC.Port)
	logger.Info("starting profiles service", "grpc_addr", addr, "kafka_group", cfg.Kafka.GroupID)

	if err := grpcTransport.Run(addr, handler); err != nil {
		logger.Error("grpc server stopped", "err", err)
		os.Exit(1)
	}
}
