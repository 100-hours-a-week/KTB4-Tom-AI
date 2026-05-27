from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_session
from schemas.llm_schema import SummaryResponse
from controllers import post_controller, comment_controller ,llm_controller

router = APIRouter(tags=["llm"])

# 게시글 요약
@router.get("/posts/{post_id}/summary", response_model=SummaryResponse)
async def summarize_post(post_id: int, db: Session = Depends(get_session)):
    post = post_controller.get_one_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return await llm_controller.summarize_post(post)

# 댓글 요약
@router.get("/posts/{post_id}/comments/{comment_id}/summary", response_model=SummaryResponse)
async def summarize_comment(post_id: int, comment_id: int, db: Session = Depends(get_session)):
    comment = comment_controller.get_comment(db, post_id, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return await llm_controller.summarize_comment(comment)
