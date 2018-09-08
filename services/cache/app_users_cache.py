from .base import cache_base

CACHE_PREFIX = 'APPUSERS_'

class AppUsersCache(cache_base.CacheBase):
    def __init__(self):
        super(AppUsersCache, self).__init__(CACHE_PREFIX)
        