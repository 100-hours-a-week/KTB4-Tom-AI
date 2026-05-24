from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import ForeignKey, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
from contextlib import asynccontextmanager
import httpx


# ----- LLM 설정 -----
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
OLLAMA_MODEL = "gemma4:e2b"

SYSTEM_PROMPT = (
    "너는 한국어 텍스트 요약 전문가야. "
    "주어진 글의 핵심 내용을 2~3문장 이내로 간결하게 요약해.\n\n"
    "규칙:\n"
    "- 원문에 없는 내용은 절대 추가하지 마.\n"
    "- 글쓴이의 주장이나 결론을 빠뜨리지 마.\n"
    "- 요약문만 출력하고, '요약:' 같은 접두사나 부가 설명은 붙이지 마.\n"
    "- 한국어로 답해."
)

# ----- 스키마 설계 -----
# 게시글 스키마
class PostCreate(BaseModel):
    title: str
    content: str
    author: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostRead(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}

# 댓글 스키마
class CommentCreate(BaseModel):
    content: str
    author: str

class CommentUpdate(BaseModel):
    content: str | None = None

class CommentRead(BaseModel):
    id: int
    post_id: int
    content: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}

# LLM 스키마
class SummaryResponse(BaseModel):
    target_type: str
    target_id: int
    summary: str

# ----- DB 모델 정의 -----
class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    author: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE")
    )
    content: Mapped[str]
    author: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    post: Mapped["Post"] = relationship(back_populates="comments")

# ----- DB 엔진, 세션, lifespan -----
DATABASE_URL = "sqlite:///community.db"

engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# ----- Post 엔드포인트 -----
# 게시글 생성
@app.post("/posts", response_model=PostRead, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_session)):
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
@app.get("/posts", response_model=list[PostRead])
def get_all_posts(db: Session = Depends(get_session)):
    return db.scalars(select(Post)).all()

# 게시글 한 개 조회
@app.get("/posts/{post_id}", response_model=PostRead)
def get_one_post(post_id: int, db: Session = Depends(get_session)):
    post = db.scalar(select(Post).where(Post.id == post_id))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# 게시글 수정 / 지금은 put으로 부분수정도 함께
@app.put("/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, updated_post: PostUpdate, db: Session = Depends(get_session)):
    post = db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if updated_post.title is not None:
        post.title = updated_post.title
    if updated_post.content is not None:
        post.content = updated_post.content
    
    db.commit()
    db.refresh(post)
    return post

# 게시글 삭제
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_session)):
    post = db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()

# ----- Comment 엔드포인트 -----
# 댓글 생성
@app.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_session)):
    post = db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
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
@app.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def get_all_comments(post_id: int, db: Session = Depends(get_session)):
    post = db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return db.scalars(select(Comment).where(Comment.post_id == post_id)).all()

# 해당 게시글의 특정 댓글 조회
@app.get("/posts/{post_id}/comments/{comment_id}", response_model=CommentRead)
def get_comment(post_id: int, comment_id: int, db: Session = Depends(get_session)):
    comment = db.scalar(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment

# 댓글 업데이트
@app.put("/posts/{post_id}/comments/{comment_id}", response_model=CommentRead)
def update_comment(post_id: int, comment_id: int, updated_comment: CommentUpdate, db: Session = Depends(get_session)):
    comment = db.scalar(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if updated_comment.content is not None:
        comment.content = updated_comment.content
    
    db.commit()
    db.refresh(comment)
    return comment

# 댓글 삭제
@app.delete("/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(post_id:int, comment_id:int, db: Session = Depends(get_session)):
    comment = db.scalar(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()

# ----- LLM 호출 -----
async def request_summarize(content: str):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [            
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {e}")

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

# ----- LLM 엔드포인트 -----
# 게시글 요약
@app.get("/posts/{post_id}/summary", response_model=SummaryResponse)
async def summarize_post(post_id: int, db: Session = Depends(get_session)):
    post = db.scalar(select(Post).where(Post.id == post_id))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    text = f"제목: {post.title}\n본문: {post.content}"
    summary = await request_summarize(text)

    return {
        "target_type": "post",
        "target_id": post_id,
        "summary": summary
    }

# 댓글 요약
@app.get("/posts/{post_id}/comments/{comment_id}/summary", response_model=SummaryResponse)
async def summarize_comment(post_id: int, comment_id: int, db: Session = Depends(get_session)):
    comment = db.scalar(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    summary = await request_summarize(comment.content)

    return {
        "target_type": "comment",
        "target_id": comment_id,
        "summary": summary
    }
