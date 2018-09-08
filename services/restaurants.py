import datetime

from django.db.models import Q
from django.conf import settings
from utils.app_logger import get_logger
from domain.models import Restaurant
from .cache.restaurants_cache import RestaurantsCache
from .appuser_service import AppUserService
from .base.service_base import ServiceBase
from .pagination_service import PaginationService, Pager
from .cloudinary_service import upload
from .google_maps import get_latlng

logger = get_logger(__name__)

class RestaurantsService(ServiceBase):
    def __init__(self):
        self.cache = RestaurantsCache()
        super(RestaurantsService, self).__init__(Restaurant)

    def __fmt_address__(self, restaurant):
        formatted = restaurant.address_line1
        if restaurant.address_line2.strip() != '':
            formatted += ', ' + restaurant.address_line2

        formatted += ', ' + restaurant.suburb + ', ' + restaurant.city
        return formatted

    def get_queryset(self):
        return Restaurant.objects.all()

    def check_admin(self, appuser_id, restaurant_id):
        cache_key = f'check_admin?appuser_id={appuser_id}&restaurant_id={restaurant_id}'
        is_admin = self.cache.get(cache_key, None)

        if is_admin != None:
            return is_admin

        q = Q()
        q &= Q(appuser_id = appuser_id)
        q &= Q(id = restaurant_id)

        is_admin = Restaurant.objects.filter(q).exists()
        self.cache.set(cache_key, is_admin)

        return is_admin

    def create(self, appuser_id, banner, **kwargs):
        logger.info(f'Creating restaurant for appuser {appuser_id}')
        try:
            upload_result = upload(banner)
            if not upload_result:
                return None
            kwargs['appuser_id'] = appuser_id
            restaurant = Restaurant(**kwargs)
            restaurant.banner_url = upload_result['secure_url']

            formatted_address = self.__fmt_address__(restaurant)

            lat, long = get_latlng(formatted_address)

            if not lat or not long:
                return None

            restaurant.latitude, restaurant.longitude = lat, long
            restaurant.save()
            logger.info(f'Restaurant created successfully with id {restaurant.id}')
            return restaurant.id
        except Exception as e:
            logger.exception(f'Could create restaurant for appuser {appuser_id}')
            return None


    def get(self, slug):
        restaurant = self.cache.search_by_id_or_slug(slug, type='slug')
        if restaurant != None:
            return restaurant
        try:
            restaurant = Restaurant.objects.prefetch_related('reviews').get(slug = slug, active = True)
            #self.cache.set(slug, restaurant)
            return restaurant
        except Restaurant.DoesNotExist:
            return None

    def get_by_appuser(self, appuser_id, page = settings.PAGE_NUMBER, size = settings.PAGE_SIZE):
        cache_key = f'get_by_appuser/?appuser_id={appuser_id}&page={page}&size={size}'

        restaurants = self.cache.get(cache_key, None)
        if restaurants != None:
            return restaurants

        q = Q()
        q &= Q(appuser_id = appuser_id)

        paginator = Pager(Restaurant.objects.all(), page, size)
        paged = PaginationService().paginate(paginator, q)

        self.cache.set(cache_key, paged, 15)

        return paged

    def update(self, id, **kwargs):
        restaurant = self.get(id)
        if restaurant == None:
            return None
        try:
            restaurant.name = kwargs.get('name')
            restaurant.address_line1 = kwargs.get('address_line1')
            restaurant.address_line2 = kwargs.get('address_line2')
            restaurant.capacity = kwargs.get('capacity')
            restaurant.tagline = kwargs.get('tagline')
            restaurant.suburb = kwargs.get('suburb')
            restaurant.city = kwargs.get('city')
            restaurant.cuisin = kwargs.get('cuisine')
            restaurant.updated = datetime.datetime.now()

            restaurant.save()

            self.cache.set(id, restaurant)

            return restaurant
        except Exception as e:
            logger.exception(f'Could not update restaurant {id}')
            return None

    def search(self, query, page = settings.PAGE_NUMBER, size = settings.PAGE_SIZE):
        if query.strip() == '':
            return []

        cache_key = f'search/?q={query}&page={page}&size={size}'

        data = self.cache.get(cache_key, None)
        '''if data != None:
            return data'''

        data = [] 

        q = Q()

        q |= Q(name__icontains = query)
        q |= Q(city__icontains = query)
        q |= Q(suburb__icontains = query)
        q |= Q(cuisine__icontains = query)
        q &= Q(operating_hours__day = 6)
        q &= Q(active = True)

        paginator = Pager(Restaurant.objects.prefetch_related('operating_hours').all(), page, size)
        paged = PaginationService().paginate(paginator, q)

        self.cache.set(cache_key, paged)

        return paged

    def is_active(self, id):
        field_list = ('active',)
        is_active = self.get_fields(field_list, **{
                'id': id
            })
        return is_active[0]['active'] if is_active else False

    def get_ids_and_status(self, appuser_id):
        cache_key = f'get_ids_and_status?appuser_id{appuser_id}'
        result = self.cache.get(cache_key)
        if result != None:
            return result

        field_list = ('id', 'active')
        result = self.get_fields(field_list, **{
                    'appuser_id': appuser_id
                })

        self.cache.set(cache_key, result, 60)

        return list(result)

    def get_by_appuser_id(self, appuser_id):
        q = Q()
        q &= Q(appuser_id = appuser_id)

        paginator = Pager(Restaurant.objects)
        paged = PaginationService().paginate(paginator, q)

        return paged

    def set_prepop(self):
        field_list = ('name', 'city', 'suburb', 'cuisine')
        prepop_data = list(self.get_fields(field_list, **{
            'active': True
        }).distinct())
        cache = []
        for data in prepop_data:
            cache.append(data['name'].strip())
            cache.append(data['suburb'].strip())
            cache.append(data['city'].strip())
            split = data['cuisine'].split(',')
            for s in split:
                cache.append(s.strip())

        self.cache.set('prepop', cache, 60 * 60 * 24)

    def query_prepop(self, query = ''):
        if not query or query.strip() == '':
            return []

        data = self.cache.get('prepop', [])

        if len(data) == 0:
            return []

        query = query.lower()

        ret = [d for d in data if query in d.lower() or query == d.lower()]

        return set(ret)

    def get_within_radius(self, lat, lng):
        
        '''
            CREATE INDEX IF NOT EXISTS restaurants_gix ON restaurants USING GIST (Geography(ST_MakePoint(longitude, latitude)));
            CREATE INDEX IF NOT EXISTS liqour_outlets_gix ON liqour_outlets USING GIST (Geography(ST_MakePoint(longitude, latitude)))
        '''
        today = datetime.datetime.today().weekday()

        query = '''SELECT 	R.ID,
                        R.NAME,
		                R.SLUG,
                        R.BANNER_URL,
                        R.CUISINE,
                        ROH.CLOSES,
                        (
                            SELECT ST_DISTANCESPHERE(
                                ST_MAKEPOINT(R.LONGITUDE, R.LATITUDE),
                                ST_MAKEPOINT(%s, %s)
                            )
                        ) AS DISTANCE
                FROM RESTAURANTS R
                INNER JOIN RESTAURANTS_OPERATING_HOURS ROH
                ON ROH.RESTAURANT_ID = R.ID
                WHERE ST_DWITHIN (
                        ST_MAKEPOINT(LONGITUDE, LATITUDE)::GEOGRAPHY,
                        ST_MAKEPOINT(%s, %s)::GEOGRAPHY,
                        %s)
                AND ROH.DAY = %s
                AND ACTIVE = TRUE
                '''

        in_radius = Restaurant.objects.prefetch_related('operating_hours').raw(
            query, [lng, lat, lng, lat, settings.SEARCH_RADIUS,today])

        return in_radius
