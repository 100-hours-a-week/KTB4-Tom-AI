from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base



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

from models.comment_model import Comment