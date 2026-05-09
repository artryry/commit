package config

import (
	"fmt"
	"os"
	"strings"
)

type Config struct {
	GRPC     GRPCConfig
	Postgres PostgresConfig
	Kafka    KafkaConfig
}

type GRPCConfig struct {
	Port string
}

type PostgresConfig struct {
	Host   string
	Port   string
	User   string
	Pass   string
	Name   string
}

type KafkaConfig struct {
	Brokers            []string
	SwipeCreatedTopic  string
	MatchCreatedTopic  string
}

func Load() *Config {
	return &Config{
		GRPC: GRPCConfig{
			Port: getEnv("GRPC_PORT", "50053"),
		},
		Postgres: PostgresConfig{
			Host: getEnv("POSTGRES_HOST", "localhost"),
			Port: getEnv("POSTGRES_PORT", "5432"),
			User: getEnv("POSTGRES_USER", "postgres"),
			Pass: getEnv("POSTGRES_PASSWORD", "postgres"),
			Name: getEnv("POSTGRES_DB", "swipes"),
		},
		Kafka: KafkaConfig{
			Brokers: strings.Split(
				getEnv("KAFKA_BROKERS", "localhost:9092"),
				",",
			),
			SwipeCreatedTopic: getEnv("KAFKA_TOPIC_SWIPE_CREATED", "swipe.created"),
			MatchCreatedTopic: getEnv("KAFKA_TOPIC_MATCH_CREATED", "match.created"),
		},
	}
}

func getEnv(key, fallback string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return fallback
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
