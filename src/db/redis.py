import aioredis
from src.config import Config

JTI_EXPIRY=3600
token_block_list=aioredis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,db=0)

async def create_jti_blocklist(jti:str)->None:
    '''
     Stores the jti (JWT ID ) not the whole token
    '''
    await token_block_list.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
        
    )

async def check_black_list(jti:str)->bool:
    '''
       Checks the JWT ID if found it will return the 
       blacklist id if not found it will return None
    
    '''
    jti= await token_block_list.get(jti)
    return jti is not None
   
   
