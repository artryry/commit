package grpcserver

import (
	"net"

	"github.com/artryry/commit/backend/services/swipes/src/internal/transport/grpc/handlers"
	pb "github.com/artryry/commit/backend/services/swipes/src/internal/transport/grpc/proto/gen"
	"google.golang.org/grpc"
)

func Run(addr string, h *handlers.SwipesHandler) error {
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		return err
	}
	s := grpc.NewServer()
	pb.RegisterSwipesServiceServer(s, h)
	return s.Serve(lis)
}
