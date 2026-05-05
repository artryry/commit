package domain

// ProfileFilter restricts which profiles are returned (combined with user ID list).
type ProfileFilter struct {
	UserIDs []int64

	RelationshipType *string
	AgeFrom          *int64
	AgeTo            *int64
	City             *string
	Sign             *string
	Tags             []string
}
