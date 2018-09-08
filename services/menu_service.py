from django.db.models import Q, Prefetch
from .base.service_base import ServiceBase
from domain.models import RestaurantMenuItemCategory, MenuItem, OptionCategory, RestaurantMenuItemOption, RestaurantMenuItem
from .cache.menu_cache import MenuCache

class MenuService(ServiceBase):
    def __init__(self):
        self.cache = MenuCache()

    def get_queryset(self):
        return OptionCategory.objects.all

    def get(self, id):
        try:
            menu_item = MenuItem.objects.get(pk = id)
            return menu_item
        except MenuItem.DoesNotExist:
            return None

    def get_menu(self, name):
        cache_key = f'get_menu/?name={name}'
        menu = self.cache.get(cache_key)
        if menu != None:
            return menu

        q = Q()
        q &= Q(restaurant__slug = name)
        menu = list(RestaurantMenuItemCategory.objects \
                        .prefetch_related(Prefetch('menu_items')) \
                        .filter(restaurant__slug = name).all())

        self.cache.set(cache_key, menu, 60)
        return menu

    def get_options(self, restaurant, menu_item):
        cache_key = f'get_options/?restaurant={restaurant}&menu_item={menu_item}'

        options = self.cache.get(cache_key, None)
        if options != None:
            return options

        q = Q()
        q &= Q(menu_item__slug = menu_item)
        q &= Q(restaurant__slug = restaurant)
        q &= Q(option_category__active = True)
        options = list(RestaurantMenuItemOption.objects\
                        .prefetch_related('option_category__options')\
                        .select_related('menu_item', 'option_category', 'restaurant')\
                        .filter(q))

        self.cache.set(cache_key, options)
        return options

    def create_menu_item(Self, **kwargs):
        try:
            menu_item = MenuItem()
            menu_item.category = kwargs.get('category')
            menu_item.name = kwargs.get('name')
            menu_item.price = kwargs.get('price')
            menu_item.save()
            return menu_item.id
        except Exception:
            return -99

    def update_menu_item(self, id, **kwargs):
        menu_item = self.get(id)
        if menu_item == None:
            return False

        menu_item.name = kwargs.get('name')
        menu_item.price = kwargs.get('price')
        menu_item.active = kwargs.get('active')

        menu_item.save()

        return True

    def create_category(self, **kwargs):
        category = Category()
        category.name = kwargs.get('name')
        category.restaurant = kwargs.get('restaurant')
        category.save()
        return category

    def get_menu_items_by_restaurant(self, restaurant_id):
        cache_key = f'get_menu_items_by_restaurant?restaurant_id={restaurant_id}'
        menu_items = self.cache.get(cache_key)

        if menu_items != None:
            return menu_items

        menu_items = list(RestaurantMenuItem.objects.select_related('category').filter(category__restaurant_id = restaurant_id))

        self.cache.set(cache_key, menu_items)

        return menu_items
