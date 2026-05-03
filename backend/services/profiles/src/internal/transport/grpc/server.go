package grpc

import (
	"net"

	"github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc/handlers"
	pb "github.com/artryry/commit/backend/services/profiles/src/internal/transport/grpc/proto/gen"
	"google.golang.org/grpc"
)

func Run(listenAddr string, handler *handlers.ProfileHandler) error {
	lis, err := net.Listen("tcp", listenAddr)
	if err != nil {
		return err
	}

	server := grpc.NewServer()

	pb.RegisterProfileServiceServer(server, handler)

	return server.Serve(lis)
}
