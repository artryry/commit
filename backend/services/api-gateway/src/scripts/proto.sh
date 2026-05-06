#!/bin/bash

set -e

PROFILE_PROTO_DIR="internal/transport/grpc/profiles/proto"
PROFILE_OUT_DIR="internal/transport/grpc/profiles/proto/gen"

REC_PROTO_DIR="internal/transport/grpc/recommendations/proto"
REC_OUT_DIR="internal/transport/grpc/recommendations/proto/gen"

echo "Generating profile protobuf files..."

protoc \
  --proto_path=$PROFILE_PROTO_DIR \
  --go_out=$PROFILE_OUT_DIR \
  --go_opt=paths=source_relative \
  --go-grpc_out=$PROFILE_OUT_DIR \
  --go-grpc_opt=paths=source_relative \
  $PROFILE_PROTO_DIR/profile.proto

echo "Generating recommendation protobuf files..."

protoc \
  --proto_path=$PROFILE_PROTO_DIR \
  --proto_path=$REC_PROTO_DIR \
  --go_out=$REC_OUT_DIR \
  --go_opt=paths=source_relative \
  --go-grpc_out=$REC_OUT_DIR \
  --go-grpc_opt=paths=source_relative \
  $REC_PROTO_DIR/recommendation.proto

echo "Proto generation completed."
