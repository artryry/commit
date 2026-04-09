package handlers

type Handlers struct {
	Auth *authHandlers
}

func NewHandlers() *Handlers {
	return &Handlers{Auth: newAuthHandlers()}
}
