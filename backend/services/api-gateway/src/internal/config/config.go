package config

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"os"
)

type Config struct {
	Port                string
	Address             string
	AuthServiceURL      string
	ProfileServiceGRPC  string
	JWTPublicKey        *rsa.PublicKey
}

func Load() *Config {
	return &Config{
		Port:               getEnv("PORT", "8080"),
		Address:            getEnv("ADDRESS", "0.0.0.0"),
		AuthServiceURL:     getEnv("AUTH_SERVICE_URL", ""),
		ProfileServiceGRPC: getEnv("PROFILE_SERVICE_GRPC_ADDR", "localhost:50051"),
		JWTPublicKey:       getJWTPublicKey("JWT_PUBLIC_KEY_PATH", ""),
	}
}

func getEnv(key, fallback string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return fallback
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
