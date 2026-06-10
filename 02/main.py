from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import Base, engine
from routers import post_router, comment_router, llm_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(llm_router.router)
