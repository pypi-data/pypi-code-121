# from hamunafs.utils.redisutil import XRedisAsync

# import asyncio

# redis = XRedisAsync('cache.ai.hamuna.club', '1987yang', 6379)

# asyncio.run(redis.zadd('1', '2', 3))
import asyncio
from aiobotocore.session import get_session
from botocore.client import Config
from aiofile import async_open
from async_exit_stack import AsyncExitStack

async def main():
    session = get_session()
    async with session.create_client('s3',
                                use_ssl=False,
                                aws_secret_access_key='1987yang',
                                aws_access_key_id='hmcz', 
                                config=Config(signature_version="s3v4"),
                                endpoint_url='http://localhost:9000') as client:
        resp = await client.put_object(Bucket='tmps',
                                            Key='temp1.txt',
                                            Body='test'.encode())
        resp = await client.delete_object(Bucket='tmps', Key='temp1.txt')
        pass

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
