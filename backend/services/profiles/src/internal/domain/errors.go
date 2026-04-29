package domain

import "fmt"

type ErrProfileNotFound struct {
	UserId int64
}

func (e ErrProfileNotFound) Error() string {
	return fmt.Sprintf("profile %d not found", e.UserId)
}
