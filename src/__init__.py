from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.books.routes import book_router
from src.auth.auth_router import auth_router
from src.reviews.review_routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def lifespan(app:FastAPI):
    # Startup code
    print("Starting up...")
    print(init_db.__doc__)
    await init_db()
    yield
    # Shutdown code
    print("Shutting down...")

version="v1"
app = FastAPI(
    title="Bookly",
    description="A simple book management API",
    version=version,
    lifespan=lifespan,
)



app.include_router(book_router,prefix=f"/api/{version}/books",tags=["books"])
app.include_router(auth_router,prefix=f"/api/{version}/auth",tags=["auth"])
app.include_router(review_router,prefix=f"/api/{version}/review",tags=["review"])
