import json
import redis
import numpy as np
from redis import asyncio as aioredis
from models import IMUData, IMUMessage
from message_broker import RedisMessageBroker


# class RedisWorker:

#     def __init__(self, headers: list[str], redis_db: redis.Redis = redis.Redis(host='localhost', port=6379, decode_responses=True, db=0)
#                  ) -> None:
#         self.r = redis_db
#         self.headers = headers

#     def read_imu_data_from_redis(self, imu_n):
#         accels = np.zeros(3)
#         gyros = np.zeros(3)
#         headers = self.headers
#         redis_db = self.r
#         def get_imu(x): return f"{imu_n}" in x
#         imu_headers = filter(get_imu, headers)

#         for header in imu_headers:
#             value = redis_db.lpop(header)
#             if value is None:
#                 return value

#             val = float(value)
#             if "acc" in header:
#                 if " x" in header:
#                     accels[2] = val
#                 elif " y" in header:
#                     accels[1] = val
#                 elif " z" in header:
#                     accels[0] = val
#             if "gyr" in header:
#                 if " x" in header:
#                     gyros[2] = val
#                 elif " y" in header:
#                     gyros[1] = val
#                 elif " z" in header:
#                     # TODO: a bug here, z is not reading
#                     gyros[0] = val
#         # data is mixed up, don't worry

#         return gyros, accels


class AsyncRedisWorker:
    def __init__(
            self,
            redis_db: aioredis.Redis = aioredis.from_url("redis://localhost:6379/0"),
            ) -> None:
        self.r = redis_db
        self.broker = RedisMessageBroker(redis_db)
        # By default, read from the last key. Skip old data.
        self.last_id = "$"

    async def subscribe(self, channel: str = "imu_data", block: int = 5, count=10):
        async for last_id, messages in self.broker.asubscribe_grouped(channel, self.last_id, block, count=count):
            self.last_id = last_id
            if len(messages) > 0:
                last_message = messages[-1]
                data = IMUMessage.from_json(json.loads(last_message))
                yield data
