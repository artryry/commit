package grpc

import (
	"net"

	"github.com/artryry/commit/services/profiles/src/internal/transport/grpc/handlers"
	pb "github.com/artryry/commit/services/profiles/src/internal/transport/grpc/proto/gen"
	"google.golang.org/grpc"
)

func Run(handler *handlers.ProfileHandler) error {
	lis, err := net.Listen("tcp", ":50051") // CHANGE PORTS!
	if err != nil {
		return err
	}

	server := grpc.NewServer()

	pb.RegisterProfileServiceServer(server, handler)

	return server.Serve(lis)
}
