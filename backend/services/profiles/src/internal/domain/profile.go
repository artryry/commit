package domain

type Image struct {
	Id  int64  `json:"id"`
	Url string `json:"url"`
}

type RelationshipType string

const (
	SearchForUnspecified  RelationshipType = "UNSPECIFIED"
	SearchForFriendship   RelationshipType = "FRIENDSHIP"
	SearchForRelationship RelationshipType = "RELATIONSHIP"
	SearchForNetworking   RelationshipType = "NETWORKING"
)

var RelationshipTypeMapper = map[string]RelationshipType{
	"UNSPECIFIED":  SearchForUnspecified,
	"FRIENDSHIP":   SearchForFriendship,
	"RELATIONSHIP": SearchForRelationship,
	"NETWORKING":   SearchForNetworking,
}

type Profile struct {
	UserId           int64
	Username         string
	Avatar           *Image
	Bio              string
	Age              int64
	Sign             string
	City             string
	SearchFor        string
	RelationshipType string
	Tags             []string
	Images           []*Image
}
