package common

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"os"

	"github.com/artryry/commit/services/api-gateway/src/clients/auth"
)

type Keys struct {
	PublicKey *rsa.PublicKey
}

func NewKeys(authClient *auth.Client) *Keys {
	pbk, err := loadPublicKey(PublicKeyPath)
	if err != nil {
		panic(err)
	}

	return &Keys{
		PublicKey: pbk,
	}
}

func loadPublicKey(path string) (*rsa.PublicKey, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(data)
	if block == nil {
		return nil, fmt.Errorf("failed to parse PEM block")
	}

	pub, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return nil, err
	}

	publicKey, ok := pub.(*rsa.PublicKey)
	if !ok {
		return nil, fmt.Errorf("not RSA public key")
	}

	return publicKey, nil
}
