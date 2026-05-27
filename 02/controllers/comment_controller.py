from sqlalchemy import select
from sqlalchemy.orm import Session
from models.comment_model import Comment
from models.post_model import Post
from schemas.comment_schema import CommentCreate, CommentUpdate


# 댓글 생성
def create_comment(db: Session, post_id: int, payload: CommentCreate):
    comment = Comment(
        post_id = post_id,
        content = payload.content,
        author = payload.author
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

# 해당 게시글의 모든 댓글 조회
def get_all_comments(db: Session, post_id: int):
    return db.scalars(select(Comment).where(Comment.post_id == post_id)).all()

# 해당 게시글의 특정 댓글 조회
def get_comment(db: Session, post_id: int, comment_id: int):
    return db.scalar(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))

# 댓글 업데이트
def update_comment(db: Session, comment: Comment, updated_comment: CommentUpdate):
    if updated_comment.content is not None:
        comment.content = updated_comment.content
    
    db.commit()
    db.refresh(comment)
    return comment

# 댓글 삭제
def delete_comment(db: Session, comment: Comment):
    
    db.delete(comment)
    db.commit()
