package clients

import "github.com/artryry/commit/services/api-gateway/src/clients/auth"

type Clients struct {
	Auth *auth.Client
}

func NewClients() *Clients {
	return &Clients{Auth: &auth.Client{}}
}
