from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from backend.config import setting

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, role: str | None = None) -> str:
    payload = {
        "sub": subject,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, setting.SECRET_KEY, algorithm=setting.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])