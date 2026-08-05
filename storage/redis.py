import os
try:
    import redis
except Exception:
    redis = None
class RedisClient:
    def __init__(self,url):
        self.url = url or os.getenv("REDIS_URL")
        self.client = redis.from_url(self.url) if (redis and self.url) else None
    def set(self, key, value, ex=None):
        if self.client:
            self.client.set(key, value, ex=ex)

    def get(self, key):
        return self.client.get(key) if self.client else None
