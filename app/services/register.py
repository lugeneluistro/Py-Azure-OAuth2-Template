from fastapi import APIRouter, HTTPException, status
from msal import ConfidentialClientApplication
import msal
import requests
from requests.exceptions import HTTPError
import logging
from decouple import config
from ..utils.constants import *
from app.models.user_dto import UserDTO


router = APIRouter(tags=['Authentication'])

logging.basicConfig(level=logging.INFO)

# Azure AD Configuration
TENANT_DOMAIN = config('AZURE_AD_B2C_DOMAIN')
TENANT_ID = config('AZURE_AD_B2C_TENANT_ID')
CLIENT_ID = config('AZURE_AD_B2C_CLIENT_ID')
CLIENT_SECRET = config('AZURE_AD_B2C_CLIENT_SECRET')
AUTHORITY = f"{AZURE_AD_B2C_AUTHORITY}/{TENANT_ID}"
SCOPE = [AZURE_AD_B2C_SCOPE]
ENDPOINT = f"{AUTHORITY}{AZURE_AD_B2C_OAUTH2_URI_SUFFIX}"
USERS_URI = AZURE_AD_B2C_USERS_URI
PUBLIC_KEY = config('AZURE_AD_B2C_PUBLIC_KEY')
ROPC_URI = config('AZURE_AD_B2C_USER_FLOW')
KUBER_GATEWAY = config('KUBER_GATEWAY')
EXTENDED_CLIENT_ID = config("AZURE_B2C_EXTENDED_CLIENT_ID")

v1prefix = "v1"

cca = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

# MSAL Confidential Client Application
client_app = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)


def get_access_token():
    # Acquire token for the app
    token_response = client_app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to acquire token")

def register_azure(userObj: UserDTO):
    
    access_token = get_access_token()
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    extended_id = str(f"{EXTENDED_CLIENT_ID}").replace("-","")

    create_user_json = {
        f"extension_{extended_id}_extendedField1": "_extendedField1",
        f"extension_{extended_id}_extendedField2": "_extendedField2",
        "displayName": f"{userObj.first_name} {userObj.last_name}",
        "mail": userObj.email,
        "givenName": userObj.first_name,
        "surname": userObj.last_name,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": False,
            "forceChangePasswordNextSignInWithMfa": False,
            "password": userObj.password
        },
        "accountEnabled": True,
        "mailNickname": f"{userObj.first_name}.{userObj.last_name}",
        "identities": [
            {
                "signInType": "emailAddress",
                "issuerAssignedId": userObj.email,
                "issuer": TENANT_DOMAIN
            }
        ]
    }

    try:
        response = requests.post(USERS_URI, headers=headers, json=create_user_json)

        response.raise_for_status()

        return {"message": "User registered successfully", "data": response.json()}

    except HTTPError as http_err:
        error_message = "An HTTP error occurred."
        try:
            error_details = response.json()
            error_message += f" Details: {error_details}"
        except ValueError:
            
            error_message += f" Response text: {response.text}"
        
        print(error_message)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        return {"error": "Unexpected error occurred", "details": str(ex)}