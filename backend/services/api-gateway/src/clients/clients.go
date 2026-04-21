package clients

import "github.com/artryry/commit/services/api-gateway/src/clients/auth"

type Clients struct {
	Auth *auth.GRPCClient
}

func NewClients() *Clients {
	return &Clients{Auth: &auth.GRPCClient{}}
}
