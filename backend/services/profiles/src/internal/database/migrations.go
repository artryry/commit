package database

import (
	"errors"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/pgx"
	_ "github.com/golang-migrate/migrate/v4/source/file"

	"github.com/artryry/commit/services/profiles/src/internal/config"
	"github.com/artryry/commit/services/profiles/src/internal/logger"
)

func RunMigrations(
	cfg *config.Config,
) error {

	m, err := migrate.New(
		"file://internal/database/migrations",
		cfg.Postgres.DSN()+"?sslmode=disable",
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
