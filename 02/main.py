from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import httpx

app = FastAPI()

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

# LLM 스키마
class SummaryResponse(BaseModel):
    target_type: str
    target_id: int
    summary: str

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
async def summarize_post(post_id: int):
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    text = f"제목: {post['title']}\n본문: {post['content']}"
    summary = await request_summarize(text)

    return {
        "target_type": "post",
        "target_id": post_id,
        "summary": summary
    }

# 댓글 요약
@app.get("/posts/{post_id}/comments/{comment_id}/summary", response_model=SummaryResponse)
async def summarize_comment(post_id: int, comment_id: int):
    comment = comments.get(comment_id)
    if (not comment) or (comment["post_id"] != post_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    
    summary = await request_summarize(comment["content"])

    return {
        "target_type": "comment",
        "target_id": comment_id,
        "summary": summary
    }
