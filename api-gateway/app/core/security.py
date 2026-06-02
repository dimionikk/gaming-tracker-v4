from jose import JWTError, jwt

from app.core.config import settings


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY.replace("\\n", "\n"),
            algorithms=["RS256"]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid token")