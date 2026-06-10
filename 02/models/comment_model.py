from datetime import datetime
from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.post_model import Post


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
