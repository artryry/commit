#!/bin/bash

protoc \
  --proto_path=. \
  --go_out=services/api-gateway/src/clients/auth \
  --go-grpc_out=services/api-gateway/src/clients/auth \
  ./proto/auth.proto