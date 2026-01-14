from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config

engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
)


async def init_db():
    '''
    This function is used to connect to the database and create all tables.
    '''
    async with engine.begin() as conn:
        from src.db.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)

# Define the dependency injection function for getting the database engine
async def get_session()->AsyncSession:
    Session=sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session

'''
How the Lifecycle Works
Request Starts: FastAPI calls get_session().

Creation: The Session is instantiated and the async with block opens.

Handoff: The yield sends the active session to your database operation (like a GET or POST request).

Operation: Your code uses the session to query or save data.

Cleanup: Once your code is done, control returns here. The async with block exits, automatically closing the session and returning the connection to the pool.

'''