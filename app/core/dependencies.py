from psycopg_pool import AsyncConnectionPool
from app.core.config import settings
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# Global connection pool
pool = None

async def get_db_pool() -> AsyncConnectionPool:
    global pool
    if pool is None:
        # Standardize URL for psycopg
        url = settings.database_url.replace("postgresql+psycopg://", "postgresql://")
        pool = AsyncConnectionPool(
            conninfo=url,
            max_size=20,
            kwargs={"autocommit": True} 
        )
    return pool

async def get_checkpointer() -> AsyncPostgresSaver:
    pool = await get_db_pool()
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup() # Ensures checkpointer tables exist natively
    return checkpointer
