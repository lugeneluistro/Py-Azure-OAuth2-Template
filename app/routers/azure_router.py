from fastapi import APIRouter, Depends, Header
from app.models.user_dto import UserDTO
from app.services.register import register_azure
from ..utils.constants import *
from typing import Annotated, List, Union
from decouple import config
from ..services.auth import get_token
from ..services.token import get_current_active_user

router = APIRouter(tags=['Authentication'])

CLIENT_ID = config('AZURE_AD_B2C_CLIENT_ID')

@router.post("/register")
async def register_user(userObj: UserDTO) -> dict:

    return register_azure(userObj)


@router.post("/login")
async def get_token(user_login: UserDTO) -> dict:
    return get_token(user_login)


@router.get("/test-secured-api")
async def getTransaction(current_user: Annotated[UserDTO, Depends(get_current_active_user)]):
    return "You've accessed a secured API using verified token from Azure AD. Congrats!"