package clients

import "github.com/artryry/commit/services/api-gateway/src/clients/profiles"

type Clients struct {
	profiles *profiles.ProfileClient
}

func NewClients() *Clients {
	return &Clients{
		profiles: profiles.NewProfileClient(),
	}
}
