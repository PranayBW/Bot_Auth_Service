import requests

from jose import jwt
from jose.exceptions import JWTError

from fastapi import HTTPException

from auth_service.config.settings import settings


async def validate_aad_token(token: str):

    try:

        # ------------------------------------------------
        # FETCH OIDC CONFIG
        # ------------------------------------------------

        oidc_url = (
            f"https://login.microsoftonline.com/"
            f"{settings.TENANT_ID}"
            f"/v2.0/.well-known/openid-configuration"
        )

        oidc = requests.get(oidc_url).json()

        jwks_uri = oidc["jwks_uri"]

        jwks = requests.get(jwks_uri).json()

        # ------------------------------------------------
        # EXTRACT TOKEN HEADER
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
                detail="AAD signing key not found"
            )

        # ------------------------------------------------
        # VALIDATE TOKEN
        # ------------------------------------------------
        print(settings.GATEWAY_API_CLIENT_ID)

        unverified = jwt.get_unverified_claims(token)
        issuer = unverified.get("iss", "")
        allowed_issuers = [
            f"https://sts.windows.net/{settings.TENANT_ID}/",
            f"https://login.microsoftonline.com/{settings.TENANT_ID}/v2.0"
        ]

        if issuer not in allowed_issuers:
            raise Exception("Invalid issuer")
        
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=f"api://{settings.GATEWAY_API_CLIENT_ID}",
            issuer=issuer
        )

        return payload

    except JWTError as ex:

        raise HTTPException(
            status_code=401,
            detail=f"AAD Token validation failed: {str(ex)}"
        )