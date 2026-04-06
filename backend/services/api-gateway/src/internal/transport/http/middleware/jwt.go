package middleware

import (
	"context"
	"log"
	"net/http"

	"github.com/artryry/commit/services/api-gateway/src/internal/common"
)

func JWT(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := r.Header.Get("Authorization")
		if token == "" {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		// TODO: Verify JWT token
		userID := "123"
		log.Printf("Verified JWT token (TODO!)")

		ctx := context.WithValue(r.Context(), common.UserIDKey, userID)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
