from .base import cache_base

CACHE_PREFIX = 'option_categories_'

class OptionCategoriesCache(cache_base.CacheBase):
    def __init__(self):
        super(OptionCategoriesCache, self).__init__(CACHE_PREFIX)