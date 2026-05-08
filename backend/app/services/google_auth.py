from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings
from fastapi import HTTPException

def verify_google_token(token: str):
    try:
        if settings.GOOGLE_CLIENT_ID is None:
            # For testing or if explicitly bypassed (not recommended in prod)
            raise ValueError("GOOGLE_CLIENT_ID is not configured")

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        return idinfo
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=400, detail=str(e))
