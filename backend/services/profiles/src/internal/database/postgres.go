package database

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/artryry/commit/services/profiles/src/internal/config"
	"github.com/artryry/commit/services/profiles/src/internal/logger"
)

func NewPostgres(
	cfg *config.Config,
) (*pgxpool.Pool, error) {

	ctx, cancel := context.WithTimeout(
		context.Background(),
		5*time.Second,
	)

	defer cancel()

	poolConfig, err := pgxpool.ParseConfig(
		cfg.Postgres.DSN(),
	)

	if err != nil {
		logger.Error("failed to parse postgres config", "error", err)

		return nil, err
	}

	// TODO: move to config
	poolConfig.MaxConns = 10
	poolConfig.MinConns = 1
	poolConfig.MaxConnLifetime = time.Hour
	poolConfig.MaxConnIdleTime = 30 * time.Minute

	var db *pgxpool.Pool

	for i := 0; i < 10; i++ {
		db, err = pgxpool.NewWithConfig(
			ctx,
			poolConfig,
		)
		if err == nil {
			break
		}

		logger.Info("retrying to connect to postgres")
		time.Sleep(2 * time.Second)
	}

	if err != nil {
		logger.Error("failed to connect to postgres", "error", err)

		panic(err)
	}

	err = db.Ping(ctx)

	if err != nil {
		logger.Error("failed to ping postgres", "error", err)

		panic(err)
	}

	logger.Info(
		"postgres connected",
		"host", cfg.Postgres.Host,
		"database name", cfg.Postgres.Name,
	)

	return db, nil
}
