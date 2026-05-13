import requests

from jose import jwt
from jose.exceptions import JWTError

from fastapi import HTTPException

from auth_service.config.settings import settings


BOTFRAMEWORK_ISSUER = (
    "https://api.botframework.com"
)


async def validate_microsoft_jwt(token: str):

    try:

        # ------------------------------------------------
        # BOTFRAMEWORK JWKS
        # ------------------------------------------------

        jwks_url = (
            "https://login.botframework.com/"
            "v1/.well-known/keys"
        )

        jwks = requests.get(jwks_url).json()

        # ------------------------------------------------
        # TOKEN HEADER
        # ------------------------------------------------

        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}

        for key in jwks["keys"]:

            if key["kid"] == unverified_header["kid"]:

                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

                break

        if not rsa_key:

            raise HTTPException(
                status_code=401,
                detail="Microsoft signing key not found"
            )

        # ------------------------------------------------
        # VALIDATE JWT
        # ------------------------------------------------

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.BOT_APP_ID,
            issuer=BOTFRAMEWORK_ISSUER
        )

        return payload

    except JWTError as ex:

        raise HTTPException(
            status_code=401,
            detail=f"Microsoft JWT validation failed: {str(ex)}"
        )