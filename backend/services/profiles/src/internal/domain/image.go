package domain

import "time"

type Image struct {
	Id         int64
	UserId     int64
	StorageKey string
	CreatedAt  time.Time
}
