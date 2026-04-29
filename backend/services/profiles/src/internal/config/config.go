package config

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	App      AppConfig
	GRPC     GRPCConfig
	Postgres PostgresConfig
	Kafka    KafkaConfig
}

type AppConfig struct {
	Port string
}

type GRPCConfig struct {
	Port string
}

type PostgresConfig struct {
	Host              string
	Port              string
	User              string
	Pass              string
	Name              string
	QueriesPathPrefix string
}

type KafkaConfig struct {
	Brokers               []string
	GroupID               string
	UserDeletedEventTopic string
	UserCreatedEventTopic string
}

func Load() *Config {

	err := godotenv.Load()
	if err != nil {
		log.Println(".env file not found")
	}

	return &Config{
		App: AppConfig{
			Port: getEnv("APP_PORT", "8002"),
		},

		GRPC: GRPCConfig{
			Port: getEnv("GRPC_PORT", "50051"),
		},

		Postgres: PostgresConfig{
			Host:              getEnv("POSTGRES_HOST", "localhost"),
			Port:              getEnv("POSTGRES_PORT", "5432"),
			User:              getEnv("POSTGRES_USER", "postgres"),
			Pass:              getEnv("POSTGRES_PASSWORD", "postgres"),
			Name:              getEnv("POSTGRES_DB", "profiles"),
			QueriesPathPrefix: getEnv("POSTGRES_QUERIES_PATH_PREFIX", "../../database/queries"),
		},

		Kafka: KafkaConfig{
			Brokers: strings.Split(
				getEnv("KAFKA_BROKERS", "localhost:9092"),
				",",
			),

			GroupID: getEnv(
				"KAFKA_GROUP_ID",
				"profile-service-group",
			),

			UserCreatedEventTopic: getEnv(
				"KAFKA_TOPIC_USER_CREATED_EVENT",
				"user.created",
			),
			UserDeletedEventTopic: getEnv(
				"KAFKA_TOPIC_USER_DELETED_EVENT",
				"user.deleted",
			),
		},
	}
}

func getEnv(key string, fallback string) string {
	value := os.Getenv(key)

	if value == "" {
		return fallback
	}

	return value
}

func (p PostgresConfig) DSN() string {
	return fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s",
		p.User,
		p.Pass,
		p.Host,
		p.Port,
		p.Name,
	)
}
