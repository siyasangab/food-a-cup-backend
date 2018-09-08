from django.core.cache import cache
from services.pagination_service import PagedCollection

class CacheBase():
    '''
        The base cache class
    '''
    
    def __init__(self, prefix):
        '''
            Constructor

            @prefix is the cache prefix to use
        '''
        self.prefix = prefix
        

    def get(self, key, default=None):
        '''
            Get a value from the cache by
        '''

        print(f'Getting {key} from cache')
        return cache.get(f'{self.prefix}{key}'.lower(), default)
    
    def set(self, key, value, timeout = 15):
        return cache.set(f'{self.prefix}{key}'.lower(), value, timeout)

    def add_or_update(self, key, value):
        cached = self.get(key.lower(), None)
        if cached == None:
            cached = []

        if value in cached:
            cached.remove(value)
            cached.append(value)
        else:
            cached.append(value)
        self.set(key, cached)

    