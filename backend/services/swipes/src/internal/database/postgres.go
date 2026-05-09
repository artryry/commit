package database

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/artryry/commit/backend/services/swipes/src/internal/config"
	"github.com/artryry/commit/backend/services/swipes/src/internal/logger"
)

func NewPostgres(cfg *config.Config) (*pgxpool.Pool, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	pc, err := pgxpool.ParseConfig(cfg.Postgres.DSN())
	if err != nil {
		return nil, err
	}
	pc.MaxConns = 10

	var db *pgxpool.Pool
	for i := 0; i < 10; i++ {
		db, err = pgxpool.NewWithConfig(ctx, pc)
		if err == nil {
			break
		}
		logger.Info("retrying postgres")
		time.Sleep(2 * time.Second)
	}
	if err != nil {
		return nil, err
	}
	if err = db.Ping(ctx); err != nil {
		return nil, err
	}
	return db, nil
}
