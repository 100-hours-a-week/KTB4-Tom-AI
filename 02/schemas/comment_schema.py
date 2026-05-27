from datetime import datetime
from pydantic import BaseModel

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
    