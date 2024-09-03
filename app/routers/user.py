from fastapi import FastAPI, HTTPException, Response, status, Depends , APIRouter
from sqlalchemy.orm import Session
from .. import models , Schema ,Utils
from ..database import SessionLocal, engine, get_db

router = APIRouter(
    prefix="/users",
    tags= ['Users']
)

@router.post("/" , status_code=status.HTTP_201_CREATED , response_model=Schema.userout)
def create_user(user : Schema.user ,db: Session = Depends(get_db)):
    existing_user = db.query(models.user).filter(models.user.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email already exists: {user.email}"
        )
    hashed_password = Utils.hash(user.password)
    user.password = hashed_password
    new_user = models.user(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/{id}" ,response_model=Schema.userout)
def get_user(id : int ,db: Session = Depends(get_db)):
    user = db.query(models.user).filter(models.user.id == id).first()
    
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , 
                            detail=f"User with id {id} doesn't exists")
    
    return user