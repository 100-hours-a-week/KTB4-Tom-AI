from models.post_model import Post
from models.comment_model import Comment
from models.llm_model import request_summarize


# 게시글 요약
async def summarize_post(post: Post):    
    text = f"제목: {post.title}\n본문: {post.content}"
    summary = await request_summarize(text)

    return {
        "target_type": "post",
        "target_id": post.id,
        "summary": summary
    }

# 댓글 요약
async def summarize_comment(comment: Comment):
    summary = await request_summarize(comment.content)

    return {
        "target_type": "comment",
        "target_id": comment.id,
        "summary": summary
    }
