from .base import cache_base

CACHE_PREFIX = 'MENU_'

class MenuCache(cache_base.CacheBase):
    def __init__(self):
        super(MenuCache, self).__init__(CACHE_PREFIX)
