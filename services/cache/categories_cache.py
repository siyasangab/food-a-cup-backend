from .base import cache_base

CACHE_PREFIX = 'categories_'

class CategoriesCache(cache_base.CacheBase):
    def __init__(self):
        super(CategoriesCache, self).__init__(CACHE_PREFIX)