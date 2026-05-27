from pydantic import BaseModel
from datetime import datetime

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