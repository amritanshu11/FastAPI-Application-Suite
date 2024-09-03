from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import Schema, models, Utils ,oauth2

router = APIRouter(
    tags=['Authentication']
)

@router.post("/login" ,response_model=Schema.token)
def login(UserCredentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.user).filter(models.user.email == UserCredentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not Utils.verify(UserCredentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data = {"user_id" : user.id})
    return {"access_token": access_token , "token_type" : "bearer"}
