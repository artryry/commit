package middleware

import (
	"context"
	"crypto/rsa"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/golang-jwt/jwt/v5"

	"github.com/artryry/commit/services/api-gateway/src/internal/common"
)

func JWT(publicKey *rsa.PublicKey) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			log.Println("Verifying JWT token...")
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}

			// JWT Verification
			tokenString := strings.TrimPrefix(authHeader, "Bearer ")

			token, err := verifyJWT(tokenString, publicKey)
			if err != nil {
				http.Error(w, "invalid or expired token", http.StatusUnauthorized)
				return
			}

			// Extract claims
			claims, ok := token.Claims.(jwt.MapClaims)
			if !ok {
				http.Error(w, "invalid claims", http.StatusUnauthorized)
				return
			}

			// Extract user ID from "sub" claim
			userIDInterface, exists := claims["sub"]
			if !exists {
				http.Error(w, "missing sub claim", http.StatusUnauthorized)
				return
			}

			// JWT numbers are float64
			userIDFloat, ok := userIDInterface.(float64)
			if !ok {
				http.Error(w, "invalid sub claim type", http.StatusUnauthorized)
				return
			}

			userID := int(userIDFloat)
			log.Printf("Verified JWT token: %v", userID)

			ctx := context.WithValue(r.Context(), common.UserIDKey, userID)

			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

func verifyJWT(tokenString string, publicKey *rsa.PublicKey) (*jwt.Token, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}

		return publicKey, nil
	})

	if err != nil {
		return nil, err
	}

	if !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	return token, nil
}
