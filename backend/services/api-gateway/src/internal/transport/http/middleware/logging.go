package middleware

import (
	"log"
	"net/http"
	"time"
)

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("Started request: %s %s %v", r.Method, r.URL.Path, start.Format(time.RFC3339))
		next.ServeHTTP(w, r)
		log.Printf("Completed request: %s %s %v", r.Method, r.URL.Path, time.Since(start))
	})
}
