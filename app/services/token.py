
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_active_user(payload: dict = Depends(verify_token)):
    return payload
