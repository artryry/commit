package clients

import "github.com/artryry/commit/services/api-gateway/src/clients/profiles"

type Clients struct {
	Profiles *profiles.ProfileClient
}

func NewClients(profileGRPCAddr string) (*Clients, error) {
	profileClient, err := profiles.NewProfileClient(profileGRPCAddr)
	if err != nil {
		return nil, err
	}

	return &Clients{
		Profiles: profileClient,
	}, nil
}
