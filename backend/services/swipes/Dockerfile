FROM golang:1.25-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o swipe-service ./src/cmd/server

FROM alpine:latest

WORKDIR /app

RUN apk add --no-cache ca-certificates

COPY --from=builder /app/swipe-service .
COPY --from=builder /app/src/internal/database/migrations ./internal/database/migrations

EXPOSE 50053

CMD ["./swipe-service"]
