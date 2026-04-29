#!/bin/bash

set -e

PROTO_DIR="internal/transport/grpc/proto"
OUT_DIR="internal/transport/grpc/proto/gen"

echo "Generating protobuf files..."

protoc \
  --proto_path=$PROTO_DIR \
  --go_out=$OUT_DIR \
  --go_opt=paths=source_relative \
  --go-grpc_out=$OUT_DIR \
  --go-grpc_opt=paths=source_relative \
  $PROTO_DIR/profile.proto

echo "Proto generation completed."