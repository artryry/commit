package handlers

import (
	"context"

	"github.com/artryry/commit/backend/services/swipes/src/internal/repository"
	"github.com/artryry/commit/backend/services/swipes/src/internal/service"
	pb "github.com/artryry/commit/backend/services/swipes/src/internal/transport/grpc/proto/gen"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type SwipesHandler struct {
	pb.UnimplementedSwipesServiceServer
	svc *service.Service
}

func New(svc *service.Service) *SwipesHandler {
	return &SwipesHandler{svc: svc}
}

func (h *SwipesHandler) RecordSwipe(ctx context.Context, req *pb.RecordSwipeRequest) (*pb.RecordSwipeResponse, error) {
	if err := h.svc.RecordSwipe(ctx, req.GetViewerUserId(), req.GetTargetUserId(), req.GetLiked()); err != nil {
		if err == repository.ErrSelfSwipe {
			return nil, status.Error(codes.InvalidArgument, err.Error())
		}
		return nil, err
	}
	return &pb.RecordSwipeResponse{Success: true}, nil
}

func (h *SwipesHandler) ListMatches(ctx context.Context, req *pb.ListMatchesRequest) (*pb.ListMatchesResponse, error) {
	ids, err := h.svc.ListMatchedUserIDs(ctx, req.GetUserId())
	if err != nil {
		return nil, err
	}
	return &pb.ListMatchesResponse{MatchedUserIds: ids}, nil
}
