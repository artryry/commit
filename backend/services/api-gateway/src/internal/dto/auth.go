package dto

type AuthRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type AuthResponse struct {
	JWT          string `json:"jwt"`
	RefreshToken string `json:"refresh_token"`
}

type RegisterRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type RegisterResponse struct {
	JWT          string `json:"jwt"`
	RefreshToken string `json:"refresh_token"`
}

type RefreshRequest struct {
	RefreshToken string `json:"refresh_token"`
}

type RefreshResponse struct {
	JWT string `json:"jwt"`
}

type DeleteAccountRequest struct {
	JWT          string `json:"jwt"`
	RefreshToken string `json:"refresh_token"`
}

type DeleteAccountResponse struct {
	Success bool `json:"success"`
}
