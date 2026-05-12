package common

import (
	"fmt"
	"strconv"

	"github.com/golang-jwt/jwt/v5"
)

// SubFromMapClaims parses JWT "sub" as user id (auth may emit int or string in JSON).
func SubFromMapClaims(claims jwt.MapClaims) (int64, error) {
	raw, ok := claims["sub"]
	if !ok || raw == nil {
		return 0, fmt.Errorf("missing sub")
	}
	switch v := raw.(type) {
	case float64:
		return int64(v), nil
	case int64:
		return v, nil
	case int:
		return int64(v), nil
	case string:
		return strconv.ParseInt(v, 10, 64)
	default:
		return 0, fmt.Errorf("unsupported sub type %T", raw)
	}
}
