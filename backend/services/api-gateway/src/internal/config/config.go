package config

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"os"
	"strings"
)

type Config struct {
	Port                       string
	Address                    string
	AuthServiceURL             string
	NotificationsServiceURL    string
	ChatsServiceURL            string
	ProfileServiceGRPC         string
	RecommendationsServiceGRPC string
	SwipesServiceGRPC          string
	JWTPublicKey               *rsa.PublicKey
	// Origins allowed by browser CORS when calling the gateway (e.g. Swagger UI on :8088 → API on :18000).
	CORSAllowedOrigins []string
}

func Load() *Config {
	defaultCORS := "http://localhost:8088,http://127.0.0.1:8088,http://localhost:18000,http://127.0.0.1:18000"
	return &Config{
		Port:                       getEnv("PORT", "8080"),
		Address:                    getEnv("ADDRESS", "0.0.0.0"),
		AuthServiceURL:             getEnv("AUTH_SERVICE_URL", ""),
		NotificationsServiceURL:    getEnv("NOTIFICATIONS_SERVICE_URL", ""),
		ChatsServiceURL:            getEnv("CHATS_SERVICE_URL", ""),
		ProfileServiceGRPC:         getEnv("PROFILE_SERVICE_GRPC_ADDR", "localhost:50051"),
		RecommendationsServiceGRPC: getEnv("RECOMMENDATIONS_SERVICE_GRPC_ADDR", "localhost:50052"),
		SwipesServiceGRPC:          getEnv("SWIPES_SERVICE_GRPC_ADDR", "localhost:50053"),
		JWTPublicKey:               getJWTPublicKey("JWT_PUBLIC_KEY_PATH", ""),
		CORSAllowedOrigins:         getEnvCSV("CORS_ALLOWED_ORIGINS", defaultCORS),
	}
}

func getEnv(key, fallback string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return fallback
}

func getEnvCSV(key, fallback string) []string {
	s := strings.TrimSpace(getEnv(key, fallback))
	parts := strings.Split(s, ",")
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p != "" {
			out = append(out, p)
		}
	}
	return out
}

func getJWTPublicKey(key string, fallback string) *rsa.PublicKey {
	path := getEnv(key, fallback)
	if path == "" {
		panic("JWT public key path not provided")
	}

	pbk, err := loadPublicKey(path)
	if err != nil {
		panic(err)
	}

	return pbk
}

func loadPublicKey(path string) (*rsa.PublicKey, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(data)
	if block == nil {
		return nil, fmt.Errorf("failed to parse PEM block")
	}

	pub, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return nil, err
	}

	publicKey, ok := pub.(*rsa.PublicKey)
	if !ok {
		return nil, fmt.Errorf("not RSA public key")
	}

	return publicKey, nil
}
