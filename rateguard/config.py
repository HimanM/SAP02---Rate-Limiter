import os

class Config:
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))

    # Token Bucket settings
    REFILL_RATE = int(os.environ.get("REFILL_RATE", 1)) # Tokens added per second
    BURST_CAPACITY = int(os.environ.get("BURST_CAPACITY", 5)) # Max tokens

    # Backend
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")
