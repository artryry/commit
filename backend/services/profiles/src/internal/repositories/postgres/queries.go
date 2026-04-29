package postgres

import (
	"embed"
	"fmt"

	"github.com/artryry/commit/services/profiles/src/internal/config"
)

//go:embed queries/*.sql
var queriesFS embed.FS

var (
	createProfileQuery string
	getProfilesQuery   string
	updateProfileQuery string
	deleteProfileQuery string
)

const (
	createProfileQueryName = "create_profile.sql"
	getProfilesQueryName   = "get_profiles.sql"
	updateProfileQueryName = "update_profile.sql"
	deleteProfileQueryName = "delete_profile.sql"
)

func initQueries(cfg *config.Config) {
	createProfileQuery = loadQuery(
		fmt.Sprintf("%s%s", cfg.Postgres.QueriesPathPrefix, createProfileQueryName),
	)
	getProfilesQuery = loadQuery(
		fmt.Sprintf("%s%s", cfg.Postgres.QueriesPathPrefix, getProfilesQueryName),
	)
	updateProfileQuery = loadQuery(
		fmt.Sprintf("%s%s", cfg.Postgres.QueriesPathPrefix, updateProfileQueryName),
	)
	deleteProfileQuery = loadQuery(
		fmt.Sprintf("%s%s", cfg.Postgres.QueriesPathPrefix, deleteProfileQueryName),
	)
}

func loadQuery(path string) string {
	content, err := queriesFS.ReadFile(path)

	if err != nil {
		panic(err)
	}

	return string(content)
}
