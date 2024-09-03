from datetime import datetime, timedelta, timezone
from . import Schema , database ,models
from jose import jwt ,JWSError
from jwt.exceptions import InvalidTokenError
from fastapi import Depends ,status ,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

Oauth2_schema = OAuth2PasswordBearer(tokenUrl= 'login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("user_id"))  # Convert to string
        print("Decoded Payload:", payload)  # Debugging print statement

        if id is None:
            raise credential_exception

        token_data = Schema.tokenData(id=id)
    except JWSError as e:
        print("Token error:", str(e))  # Debugging print statement
        raise credential_exception

    return token_data





def get_current_user(token : str = Depends(Oauth2_schema),db: Session = Depends(database.get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,
                                         detail=f"Could not verify credential", headers={"WWW-Authenticate" : "Bearer"})
    
    token = verify_access_token(token , credential_exception)
    user = db.query(models.user).filter(models.user.id == token.id).first()
    return user
    