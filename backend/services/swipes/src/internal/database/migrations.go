package database

import (
	"errors"
	"strings"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/pgx"
	_ "github.com/golang-migrate/migrate/v4/source/file"

	"github.com/artryry/commit/backend/services/swipes/src/internal/config"
	"github.com/artryry/commit/backend/services/swipes/src/internal/logger"
)

func RunMigrations(cfg *config.Config) error {
	dsn := cfg.Postgres.DSN()
	dsn = strings.ReplaceAll(dsn, "postgres://", "pgx://")
	m, err := migrate.New(
		"file://internal/database/migrations",
		dsn+"?sslmode=disable",
	)
	if err != nil {
		return err
	}
	err = m.Up()
	if err != nil && !errors.Is(err, migrate.ErrNoChange) {
		return err
	}
	logger.Info("migrations applied")
	return nil
}
