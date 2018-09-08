from .base import cache_base

CACHE_PREFIX = 'GALLERYITEMS_'

class GalleryItemsCache(cache_base.CacheBase):
    def __init__(self):
        super(GalleryItemsCache, self).__init__(CACHE_PREFIX)