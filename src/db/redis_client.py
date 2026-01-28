import redis.asyncio as aioredis
from src.config import Config

JTI_EXPIRY = 3600
token_block_list = aioredis.from_url(Config.REDIS_URL)

async def create_jti_blocklist(jti: str) -> None:
    '''
     Stores the jti (JWT ID ) not the whole token
    '''
    await token_block_list.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )

async def check_black_list(jti: str) -> bool:
    '''
       Checks the JWT ID if found it will return the 
       blacklist id if not found it will return None
    
    '''
    jti = await token_block_list.get(jti)
    return jti is not None

