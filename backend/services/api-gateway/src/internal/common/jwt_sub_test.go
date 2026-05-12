package common

import (
	"testing"

	"github.com/golang-jwt/jwt/v5"
)

func TestSubFromMapClaims_stringAndFloat(t *testing.T) {
	claims := jwt.MapClaims{"sub": "3"}
	id, err := SubFromMapClaims(claims)
	if err != nil || id != 3 {
		t.Fatalf("string: %v %v", id, err)
	}
	claims2 := jwt.MapClaims{"sub": float64(3)}
	id2, err := SubFromMapClaims(claims2)
	if err != nil || id2 != 3 {
		t.Fatalf("float: %v %v", id2, err)
	}
}
