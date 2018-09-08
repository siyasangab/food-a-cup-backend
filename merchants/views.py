from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from services.option_category_service import OptionCategoryService
from utils.app_logger import get_logger
from services.restaurants import RestaurantsService
from services.category_service import CategoryService
from services.appuser_service import AppUserService
from services.menu_service import MenuService
from services.order_service import OrderService
from .permissions import *
from domain.serializers import *
from services.http_response import OK, INTERNAL_SERVER_ERROR, CREATED, BAD_REQUEST

logger = get_logger(__name__)

class AddRestaurant(CreateAPIView):
    permission_classes = (PlaceAdmin,)

    def __init__(self):
        self._restaurants_service = RestaurantsService()
        self._appuser_service = AppUserService()

    def post(self, request, *args, **kwargs):
        serializer = RestaurantCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return BAD_REQUEST(serializer.errors)

        banner = request.data.get('banner', None)

        if banner == None:
            return BAD_REQUEST('Please upload a banner.')


        newid = self._restaurants_service.create(request.appuser_id, banner, **serializer.validated_data)

        if not newid:
            return INTERNAL_SERVER_ERROR('Could not save the restaurant.')

        return OK(newid)

class UpdateRestaurant(UpdateAPIView):
    permission_classes = (PlaceAdmin, RestaurantAdmin)

    def __init__(self, *args, **kwargs):
        self._restaurants_service = RestaurantsService()

    def put(self, request, restaurant_id):
        logger.info(f'Updating restaurant {restaurant_id} with data {request.data}')
        serializer = RestaurantCreateSerializer(data = request.data)

        if not serializer.is_valid():
            logger.error(f'Validation failed, {serializer.errors}')
            return BAD_REQUEST(serializer.errors)

        updated = self._restaurants_service.update(restaurant_id, **serializer.validated_data)

        if not updated:
            msg = 'Could not update the restaurant.'
            logger.error(f'{msg}')
            return INTERNAL_SERVER_ERROR(msg)

        logger.info('Restaurant updated successfully.')
        return OK(None)

class GetRestaurants(ListAPIView):
    permission_classes = (PlaceAdmin,)

    def __init__(self):
       self._restaurants_service = RestaurantsService() 

    def get(self, request):
        restaurants = self._restaurants_service.get_by_appuser(request.appuser_id)
        resp = restaurants.serialize_data(RestaurantsListResponseSerializerAdmin)
        return Response(resp)

class AddMenuItem(CreateAPIView):
    permission_classes = (PlaceAdmin,)

    def __init__(self):
        self._menu = MenuService()

    @method_decorator(csrf_protect)
    def post(self, request):
        serializer = MenuItemCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        newid = self._menu.create_menu_item(**serializer.validated_data)
        if newid == -99:
            return INTERNAL_SERVER_ERROR('Could not save the app menu item. Please try again later.')

        return OK(newid)

class UpdateMenuItem(UpdateAPIView):
    permission_classes = (PlaceAdmin,)

    def __init__(self):
        self._menu = MenuService()

    @method_decorator(csrf_protect)
    def put(self, request, id):
        serializer = MenuItemCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        updated = self._menu.update_menu_item(id, **serializer.validated_data)

        if not updated:
            return INTERNAL_SERVER_ERROR('Could not update the app menu item. Please try again later.') 
        
        return OK()

class AddCategory(CreateAPIView):
    permission_classes = (PlaceAdmin, RestaurantAdmin)

    def __init__(self):
        self._menu = MenuService()

    @method_decorator(csrf_protect)
    def post(self, request, restaurant_id):
        serializer = CategoryCreateSerializer(data = request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        self._menu.create_category(**serializer.validated_data)
        return Response(status = status.HTTP_201_CREATED)

class UpdateCategory(UpdateAPIView):
    permission_classes = (PlaceAdmin, ChangeCategory)

    def __init__(self):
        self._categories = CategoryService()

    @method_decorator(csrf_protect)
    def put(self, request, id):
        serializer = CategoryUpdateSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        updated = self._categories.update(id, **serializer.validated_data)

        if updated:
            return OK()

        return INTERNAL_SERVER_ERROR('Could not update the category, please try again later.')

class GetOptionCategories(ListAPIView):
    permission_classes = (PlaceAdmin, RestaurantAdmin)

    def __init__(self):
        self._option_category_service = OptionCategoryService()

    def get(self, request, restaurant):
        option_categories = self._option_category_service.get_by_restaurant(restaurant)   
        serializer = OptionCategoryListSerializer(option_categories, many = True)
        return OK(serializer.data)

class AddOptionCategory(CreateAPIView):
    permission_classes = (PlaceAdmin, RestaurantAdmin)

    def __init__(self):
        self._option_category_service = OptionCategoryService()

    @method_decorator(csrf_protect)
    def post(self, request):
        serializer = OptionCategoryCreateSerializer(data = request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        id = self._option_category_service.create(**serializer.validated_data)

        if id == -99:
            return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(id, status = status.HTTP_201_CREATED)


class GetOrders(ListAPIView):
    permission_classes = (PlaceAdmin, RestaurantAdmin)

    def __init__(self):
        self._order_service = OrderService()

    def get(self, request, restaurant_id):
        orders = self._order_service.get_todays_pending_orders(restaurant_id)
        serializer = OrderResponseSerializer(orders, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class AcceptOrder(UpdateAPIView):
    permission_classes = (PlaceAdmin, AcceptOrder)

    def __init__(self):
        self._order_service = OrderService()

    @method_decorator(csrf_protect)
    def put(self, request, order_id):
        accepted, msg = self._order_service.accept_order(order_id)

        if not accepted:
            return BAD_REQUEST(msg)

        return OK('')

class UpdateOptionCategory(UpdateAPIView):
    permission_classes = (PlaceAdmin, ChangeOptionCategory)

    def __init__(self):
        self._option_category_service = OptionCategoryService()

    @method_decorator(csrf_protect)
    def put(self, request, id):
        serializer = OptionCategoryUpdateSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        updated = self._option_category_service.update(**serializer.validated_data)

        if not updated:
            return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status = status.HTTP_200_OK)
