package postgres

import (
	"embed"
	"fmt"

	"github.com/artryry/commit/backend/services/profiles/src/internal/config"
)

//go:embed queries/*.sql
var queriesFS embed.FS

var (
	createProfileQuery string
	fillProfileQuery   string
	getProfilesQuery   string
	getProfilesWithFilterQuery string
	updateProfileQuery string
	deleteProfileQuery string

	attachTagsQuery        string
	createImageQuery       string
	deleteImageQuery       string
	createTagsQuery        string
	detachProfileTagsQuery string
)

const (
	createProfileQueryName = "create_profile.sql"
	fillProfileQueryName   = "fill_profile.sql"
	getProfilesQueryName   = "get_profiles.sql"
	getProfilesWithFilterQueryName = "get_profiles_with_filter.sql"
	updateProfileQueryName = "update_profile.sql"
	deleteProfileQueryName = "delete_profile.sql"

	attachTagsQueryName        = "attach_tags.sql"
	createImageQueryName       = "create_image.sql"
	deleteImageQueryName       = "delete_image.sql"
	createTagsQueryName        = "create_tags.sql"
	detachProfileTagsQueryName = "detach_profile_tags.sql"
)

func initQueries(cfg *config.Config) {
	createProfileQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, createProfileQueryName),
	)
	fillProfileQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, fillProfileQueryName),
	)
	getProfilesQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, getProfilesQueryName),
	)
	getProfilesWithFilterQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, getProfilesWithFilterQueryName),
	)
	updateProfileQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, updateProfileQueryName),
	)
	deleteProfileQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, deleteProfileQueryName),
	)

	attachTagsQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, attachTagsQueryName),
	)
	createImageQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, createImageQueryName),
	)
	deleteImageQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, deleteImageQueryName),
	)
	createTagsQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, createTagsQueryName),
	)
	detachProfileTagsQuery = loadQuery(
		fmt.Sprintf("%s/%s", cfg.Postgres.QueriesPathPrefix, detachProfileTagsQueryName),
	)
}

func loadQuery(path string) string {
	content, err := queriesFS.ReadFile(path)

	if err != nil {
		panic(err)
	}

	return string(content)
}
