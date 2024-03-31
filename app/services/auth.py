from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests 
from jose import JWTError, jwt, ExpiredSignatureError
from decouple import config
import httpx
from jwt.algorithms import RSAAlgorithm
from app.models.user_dto import UserDTO
from ..utils.constants import *

router = APIRouter(tags=['Authentication'])

CLIENT_ID = config('AZURE_AD_B2C_CLIENT_ID')
ROPC_URI=config('AZURE_AD_B2C_USER_FLOW')
B2C_JWK = config('AZURE_AD_B2C_JWK')
B2C_FLOW = config('AZURE_AD_B2C_FLOW')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def verify_token(token: str = Depends(oauth2_scheme)):
    cmp_url = f"{B2C_JWK}={B2C_FLOW}"
    response = requests.get(cmp_url)
    jwk_data = response.json()['keys'][0]

    # Convert JWK to PEM
    pem_key = RSAAlgorithm.from_jwk(jwk_data)

    try:
        payload = jwt.decode(token, pem_key, algorithms=[JWT_ALGORITHM], audience=config('AZURE_AD_B2C_CLIENT_ID'))
        return payload
    except ExpiredSignatureError:
        raise Exception("Token has expired.")
    except JWTError as e:
        raise Exception(f"JWT processing error: {e}")
    

async def get_token (user_login: UserDTO)-> dict:
    # Acquire token by username and password
    form_data = {
        "grant_type": OAUTH2_GRANT_TYPE,
        "scope": f"offline_access openid {CLIENT_ID}",
        "client_id": CLIENT_ID,
        "username": user_login.email,
        "password": user_login.password,
        "response_type": OAUTH2_RESPONSE_TYPE,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ROPC_URI, data=form_data, headers=OAUTH2_DEFAULT_HEADER)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_message = response.json().get("error_description", "Failed to fetch refresh token")
            raise HTTPException(status_code=response.status_code, detail=error_message)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Azure: {str(e)}")