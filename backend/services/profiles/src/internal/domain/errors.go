package domain

import (
	"fmt"
)

type ErrProfileNotFound struct {
	UserId int64
}

func (e ErrProfileNotFound) Error() string {
	return fmt.Sprintf("profile %d not found", e.UserId)
}

type ErrUnsupportedImageType struct {
}

func (e ErrUnsupportedImageType) Error() string {
	return "unsupported image type, supported types: jpeg, png, webp"
}

type ErrNoPermissions struct {
	userId int64
}

func (e ErrNoPermissions) Error() string {
	return fmt.Sprintf("user %d has no permissions", e.userId)
}
