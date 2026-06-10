from fastapi import APIRouter, HTTPException, Depends
from database import get_session
from sqlalchemy.orm import Session
from schemas.comment_schema import CommentUpdate, CommentCreate, CommentRead
from controllers import comment_controller, post_controller

router = APIRouter(tags=["comments"])

# 댓글 생성
@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_session)):
    post = post_controller.get_one_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return comment_controller.create_comment(db, post_id, payload)

# 해당 게시글의 모든 댓글 조회
@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def get_all_comments(post_id: int, db: Session = Depends(get_session)):
    post = post_controller.get_one_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return comment_controller.get_all_comments(db, post_id)

# 해당 게시글의 특정 댓글 조회
@router.get("/posts/{post_id}/comments/{comment_id}", response_model=CommentRead)
def get_comment(post_id: int, comment_id: int, db: Session = Depends(get_session)):
    comment = comment_controller.get_comment(db, post_id, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment

# 댓글 업데이트
@router.put("/posts/{post_id}/comments/{comment_id}", response_model=CommentRead)
def update_comment(post_id: int, comment_id: int, payload: CommentUpdate, db: Session = Depends(get_session)):
    comment = comment_controller.get_comment(db, post_id, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment_controller.update_comment(db, comment, payload)

# 댓글 삭제
@router.delete("/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(post_id:int, comment_id:int, db: Session = Depends(get_session)):
    comment = comment_controller.get_comment(db, post_id, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment_controller.delete_comment(db, comment)
