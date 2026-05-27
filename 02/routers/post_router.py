from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_session
from schemas.post_schema import PostCreate, PostRead, PostUpdate
from controllers import post_controller

router = APIRouter(tags=["posts"])

# 게시글 생성
@router.post("/posts", response_model=PostRead, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_session)):
    return post_controller.create_post(db, payload)

# 전체 게시글 조회
@router.get("/posts", response_model=list[PostRead])
def get_all_posts(db: Session = Depends(get_session)):
    return post_controller.get_all_posts(db)

# 게시글 한 개 조회
@router.get("/posts/{post_id}", response_model=PostRead)
def get_one_post(post_id: int, db: Session = Depends(get_session)):
    post = post_controller.get_one_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# 게시글 수정 / 지금은 put으로 부분수정도 함께
@router.put("/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_session)):
    post = post_controller.get_one_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post_controller.update_post(db, post, payload)

# 게시글 삭제
@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_session)):
    post = post_controller.get_one_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_controller.delete_post(db, post)