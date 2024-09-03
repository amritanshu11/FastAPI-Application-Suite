from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, Schema, Utils, oauth2
from ..database import SessionLocal, engine, get_db
from typing import Optional, List


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[Schema.PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = ""):
    posts = db.query(
        models.Post, 
        func.count(models.vote.post_id).label("Votes")
        ).join(
            models.vote, 
            models.vote.post_id == models.Post.id, 
            isouter=True
            ).group_by(
                models.Post.id
                ).filter(
                    models.Post.title.contains(search)
                    ).limit(limit).all()
    return posts



@router.get("/MyPost", response_model=List[Schema.PostOut])
def My_posts(db: Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
    #posts = db.query(models.Post).filter(models.Post.user_id == user_id.id).all()
    posts = db.query(
        models.Post, 
        func.count(models.vote.post_id).label("Votes")
        ).join(
            models.vote, 
            models.vote.post_id == models.Post.id, 
            isouter=True
            ).group_by(
                models.Post.id
                ).filter(
                    models.Post.user_id == user_id.id
                    ).all()
    return posts

# @router.post("/post")
# def post(new_post : dict = Body(...)): // This is the way how you can get the data from the body
#     return {"title": f"Title is : {new_post}"}


@router.post("/", status_code=status.HTTP_201_CREATED , response_model=Schema.postResponse)
def create_posts(post: Schema.post, db: Session = Depends(get_db) , user_id : int = Depends(oauth2.get_current_user)):
    new_post = models.Post(user_id = user_id.id , **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}" )
def get_post(id: str, db: Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Data not found with id : {id}")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT )
def delete_post(id: int, db: Session = Depends(get_db) , user_id : int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()
    
    if post == None:  # Use "is None" for comparison
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Data not found with id: {id}")
    if post.user_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Forbidden User")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}" , response_model=Schema.postResponse)
def Update_Post(id: int, post: Schema.post, db: Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
    updated_post = db.query(models.Post).filter(models.Post.id == id)
    postData = updated_post.first()
    if postData == None:  # Use "is None" for comparison
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Data not found with id: {id}")
    if postData.user_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Forbidden User")
    updated_post.update(post.dict(), synchronize_session=False)
    db.commit()
    return updated_post.first()