package domain

import "time"

type RelationshipType string
type Gender string

const (
	SearchForUnspecified  RelationshipType = "UNSPECIFIED"
	SearchForFriendship   RelationshipType = "FRIENDSHIP"
	SearchForRelationship RelationshipType = "RELATIONSHIP"
	SearchForNetworking   RelationshipType = "NETWORKING"

	GenderMale   = "M"
	GenderFemale = "F"
)

var RelationshipTypeMapper = map[string]RelationshipType{
	"UNSPECIFIED":  SearchForUnspecified,
	"FRIENDSHIP":   SearchForFriendship,
	"RELATIONSHIP": SearchForRelationship,
	"NETWORKING":   SearchForNetworking,
}

var GenderMapper = map[string]Gender{
	"M": GenderMale,
	"F": GenderFemale,
}

type Profile struct {
	UserId           int64
	Username         string
	Avatar           *Image
	Bio              string
	Birthday         time.Time
	Gender           Gender
	Age              int64
	Sign             string
	City             string
	SearchFor        string
	RelationshipType RelationshipType
	Tags             []string
	Images           []*Image
}
