import time
import json
import redis
from .config import Config

import os

# Initialize Redis client
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

def build_redis_key(user_id, endpoint):
    return f"rate_limit:{user_id}:{endpoint}"

# Dynamically load the Atomic Lua script
LUA_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'token_bucket.lua')
with open(LUA_SCRIPT_PATH, 'r') as file:
    TOKEN_BUCKET_LUA = file.read()

def check_rate_limit(user_id, endpoint):
    """
    Token bucket algorithm for rate limiting using Redis Lua Scripts
    to guarantee atomic evaluations and prevent race conditions.
    Returns True if request is allowed, False if rejected.
    """
    key = build_redis_key(user_id, endpoint)
    current_time = time.time()
    
    try:
        allowed = redis_client.eval(
            TOKEN_BUCKET_LUA, 
            1, 
            key, 
            Config.BURST_CAPACITY, 
            Config.REFILL_RATE, 
            current_time
        )
        return allowed == 1
    except redis.exceptions.ConnectionError:
        # If Redis is down, fail open
        print("Redis unavailable, failing open")
        return True
    except redis.exceptions.ResponseError as e:
        print(f"Redis script error: {e}")
        return True
