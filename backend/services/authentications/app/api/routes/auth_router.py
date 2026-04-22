from fastapi.routing import APIRouter


router = APIRouter(
    tags=["auth"],
)


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/login")
async def login():
    return {"message": "Login endpoint - to be implemented"}


@router.post("/register")
async def register():
    return {"message": "Register endpoint - to be implemented"}


@router.post("/refresh")
async def refresh_token():  
    return {"message": "Refresh token endpoint - to be implemented"}


@router.post("/logout")
async def logout():
    return {"message": "Logout endpoint - to be implemented"}


@router.post("/delete")
async def delete_account():     
    return {"message": "Delete account endpoint - to be implemented"}
