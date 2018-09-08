from .base import cache_base

CACHE_PREFIX = 'restaurants_'

class RestaurantsCache(cache_base.CacheBase):
    def __init__(self):
        super(RestaurantsCache, self).__init__(CACHE_PREFIX)
