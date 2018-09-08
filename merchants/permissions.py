from rest_framework import permissions
from services.appuser_service import AppUserService
from services.restaurants import RestaurantsService
from services.category_service import CategoryService
from services.option_category_service import OptionCategoryService
from services.order_service import OrderService
from services.appuser_service import AppUserService

class PlaceAdmin(permissions.BasePermission):
    def __init__(self):
        self._appuser_service = AppUserService()

    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='place_admin'):
            appuser_id = self._appuser_service.get_appuser_id_by_user_id(request.user.id)
            if not appuser_id:
                return False
            request.appuser_id = appuser_id
            return True
        return False

class RestaurantAdmin(permissions.BasePermission):
    def __init__(self):
        self.__appuser_service = AppUserService()
        self.__restaurants_service = RestaurantsService()

    def has_permission(self, request, view):
        restaurant_id = view.kwargs.get('restaurant_id')

        if restaurant_id == None:
            restaurant_id = request.data.get('restaurant_id')
            if restaurant_id == None:
                return False

        is_admin = self.__restaurants_service.check_admin(request.appuser_id, restaurant_id)

        return is_admin
            
class ChangeCategory(permissions.BasePermission):
    def __init__(self):
        self.__category_service = CategoryService()
        self.__appuser_service = AppUserService()

    def has_permission(self, request, view):
        category_id = view.kwargs.get('id')
        if category_id == None:
            return False

        if not request.user:
            return False

        appuser_id = self.__appuser_service.get_appuser_id_by_user_id(request.user.id)
        if not appuser_id:
            return False

        is_admin = self.__category_service.is_appuser_admin(appuser_id, int(category_id))

        return is_admin

class ChangeOptionCategory(permissions.BasePermission):
    def __init__(self):
        self.__option_category_service = OptionCategoryService()
        self.__appuser_service = AppUserService()

    def has_permission(self, request, view):
        option_category_id = view.kwargs.get('id')

        if option_category_id == None:
            return False

        is_admin =  self.__option_category_service.is_appuser_admin(request.appuser_id, option_category_id)

        return is_admin

class AcceptOrder(permissions.BasePermission):
    def __init__(self, *args, **kwargs):
        self._order_service = OrderService()
        self._restaurants_service = RestaurantsService()

    def has_permission(self, request, view):
        order_id = view.kwargs.get('order_id')

        restaurant_id = self._order_service.get_restaurant_id_by_orderid(order_id)
        if not restaurant_id:
            return False

        is_restaurant_admin = self._restaurants_service.check_admin(request.appuser_id, restaurant_id)

        return is_restaurant_admin

        
