from sqlalchemy import select
from sqlalchemy.orm import Session
from models.post_model import Post
from schemas.post_schema import PostCreate, PostUpdate


# 게시글 생성
def create_post(db: Session, payload: PostCreate):
    post = Post(
        title = payload.title,
        content = payload.content,
        author = payload.author
    )

    db.add(post)
    db.commit()
    db.refresh(post)
    return post

# 전체 게시글 조회
def get_all_posts(db: Session):
    return db.scalars(select(Post)).all()

# 게시글 한 개 조회
def get_one_post(db: Session, post_id: int):
    return db.scalar(select(Post).where(Post.id == post_id))

# 게시글 수정 / 지금은 put으로 부분수정도 함께
def update_post(db: Session, post: Post, updated_post: PostUpdate):
    if updated_post.title is not None:
        post.title = updated_post.title
    if updated_post.content is not None:
        post.content = updated_post.content
    
    db.commit()
    db.refresh(post)
    return post

# 게시글 삭제
def delete_post(db: Session, post: Post):
    
    db.delete(post)
    db.commit()