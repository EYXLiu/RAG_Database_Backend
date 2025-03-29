import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("NEXT_REDIS_HOST")
REDIS_PORT = os.getenv("NEXT_REDIS_PORT")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)