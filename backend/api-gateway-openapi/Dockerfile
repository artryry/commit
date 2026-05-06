# Serves OpenAPI documentation with Swagger UI. The spec is bundled read-only.
# Build:  docker build -t commit-api-docs ./api-gateway-openapi
# Run:    docker run --rm -p 8888:8080 commit-api-docs
# UI:     http://localhost:8888/
FROM swaggerapi/swagger-ui:v5.18.2

COPY openapi.yaml /openapi.yaml

ENV SWAGGER_JSON=/openapi.yaml
