from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# ----- 스키마 설계 -----
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

# ----- 메모리 저장소 -----
posts: dict[int, dict] = dict()
comments: dict[int, dict] = dict()
post_id_seq = 0
comment_id_seq = 0

# ----- Post 엔드포인트 -----
# 게시글 생성
@app.post("/posts", response_model=PostRead, status_code=201)
def create_post(post: PostCreate):
    global post_id_seq
    post_id_seq += 1
    new_post = {
        "id": post_id_seq,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "created_at": datetime.now()
    }

    posts[post_id_seq] = new_post
    return new_post

# 전체 게시글 조회
@app.get("/posts", response_model=list[PostRead])
def get_all_posts():
    return list(posts.values())

# 게시글 한 개 조회
@app.get("/posts/{post_id}", response_model=PostRead)
def get_one_post(post_id: int):
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts[post_id]

# 게시글 수정 / 지금은 put으로 부분수정도 함께
@app.put("/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, updated_post: PostUpdate):
    post = posts.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if updated_post.title is not None:
        post["title"] = updated_post.title
    if updated_post.content is not None:
        post["content"] = updated_post.content
    
    return post

# 게시글 삭제
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    post = posts.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    del posts[post_id]

    # 게시글의 댓글도 삭제
    to_delete = [cid for cid, c in comments.items() if c["post_id"] == post_id]

    for cid in to_delete:
        del comments[cid]

# ----- Comment 엔드포인트 -----
# 댓글 생성
@app.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=201)
def create_comment(post_id: int, comment: CommentCreate):
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    global comment_id_seq
    comment_id_seq += 1

    new_comment = {
        "id": comment_id_seq,
        "post_id": post_id,
        "content": comment.content,
        "author": comment.author,
        "created_at": datetime.now()
    }

    comments[comment_id_seq] = new_comment

    return new_comment

# 해당 게시글의 모든 댓글 조회
@app.get("/posts/{post_id}/comments", response_model=list[CommentRead])
def get_all_comments(post_id: int):
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return [c for c in comments.values() if c["post_id"] == post_id]

# 해당 게시글의 특정 댓글 조회
@app.get("/posts/{post_id}/comments/{comment_id}", response_model=CommentRead)
def get_comment(post_id: int, comment_id: int):
    comment = comments.get(comment_id)
    if (not comment) or (comment["post_id"] != post_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment

# 댓글 업데이트
@app.put("/posts/{post_id}/comments/{comment_id}", response_model=CommentRead)
def update_comment(post_id: int, comment_id: int, updated_comment: CommentUpdate):
    comment = comments.get(comment_id)
    if (not comment) or (comment["post_id"] != post_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    if updated_comment.content is not None:
        comment["content"] = updated_comment.content
    
    return comment

# 댓글 삭제
@app.delete("/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(post_id:int, comment_id:int):
    comment = comments.get(comment_id)
    if (not comment) or (comment["post_id"] != post_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    
    del comments[comment_id]

