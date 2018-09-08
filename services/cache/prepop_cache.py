from .base import cache_base

CACHE_PREFIX = 'PREPOP_'

class PrepopCache(cache_base.CacheBase):
    def __init__(self):
        super(PrepopCache, self).__init__(CACHE_PREFIX)
        