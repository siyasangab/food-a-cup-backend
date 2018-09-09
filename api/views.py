from django.views.decorators.cache import cache_page
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from services.order_service import OrderService
from services.menu_service import MenuService
from services.restaurants import RestaurantsService
from services.registration_service import RegistrationService
from domain.serializers import *
from domain.models import Option, OptionCategory
from .permissions import Customer, CanChangeOrder
from services.http_response import OK, INTERNAL_SERVER_ERROR, CREATED, BAD_REQUEST

# Create your views here.
class Index(RetrieveAPIView):
    '''
        Index view to ping the api
    '''
    permissions_classes = (permissions.AllowAny,)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response('PONG', status=status.HTTP_200_OK)

class Register(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    def __init__(self):
        self._registration_service = RegistrationService()

    def post(self, request):
        serializer = AppUserCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return BAD_REQUEST(serializer.errors)
        app_user = self._registration_service.create(**serializer.validated_data)
        response_serializer = AppUserResponseSerializer(app_user)
        return OK(response_serializer.data)

class GetMenu(ListAPIView):
    '''
        Get a restaurant's menu
    '''
    permission_classes = (permissions.AllowAny,)

    def __init__(self):
        self._menu = MenuService()

    decorators = [cache_page(settings.ONE_DAY), ensure_csrf_cookie]

    @method_decorator(cache_page(settings.ONE_DAY))
    def get(self, request, name):
        menu = self._menu.get_menu(name)
        serializer = RestaurantCategoryResponseSerializer(menu, many = True)
        return Response(serializer.data)

    def get_queryset(self):
        return self._menu.get_queryset()

class CreateOrder(CreateAPIView):
    '''
        Create an order
    '''
    permission_classes = (Customer,)
    def __init__(self):
        self._order_service = OrderService()

    #@method_decorator(csrf_protect)
    def post(self, request):
        serializer = OrderCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return BAD_REQUEST(serializer.errors)

        order_is_valid = self._order_service.validate(**serializer.validated_data)

        if not order_is_valid:
            return BAD_REQUEST('LMAO you\'re cheating')

        self._order_service.create(request.appuser_id, **serializer.validated_data)

        return CREATED()

class CancelOrder(UpdateAPIView):
    permission_classes = (Customer, CanChangeOrder)
    def __init__(self):
        self._order_service = OrderService()

    #@method_decorator(csrf_protect)
    def update(self, request, order_id):
        cancelled, msg = self._order_service.cancel(order_id)
        if cancelled:
            return OK()

        return BAD_REQUEST(msg)

class UpdateOrder(UpdateAPIView):
    permission_classes = (Customer, CanChangeOrder)

    def __init__(self):
        self._order_service = OrderService()
    
    #@method_decorator(cache_page(60))
    def put(self, request, order_id):     
        serializer = OrderCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return BAD_REQUEST(serializer.errors)

        order_is_valid = self._order_service.validate(**serializer.validated_data)
        if not order_is_valid:
            return BAD_REQUEST('Lol')

        updated, msg = self._order_service.update(order_id, **serializer.validated_data)

        if not updated:
            return BAD_REQUEST(msg);
        return OK('')

class SaveOrderForLater(CreateAPIView):
    def __init__(self):
        self._order_service = OrderService()

    def post(self, request):
        pass

class GetRestaurants(ListAPIView):
    permission_classes = (permissions.AllowAny,)

    def __init__(self):
        self._restaurants = RestaurantsService()

    @method_decorator(cache_page(settings.ONE_DAY))
    def get(self, request):
        q = request.query_params.get('q', None)
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size', 10)
        restaurants = self._restaurants.search(q, page, size)

        resp = restaurants.serialize_data(RestaurantsListResponseSerializer)

        return Response(resp)

class GetWithinRadius(ListAPIView):
    '''
        Get restaurants within a radius of user's latitude and longitude. The radius is configured in settings.
    '''
    permission_classes = (permissions.AllowAny,)   

    def __init__(self, **kwargs):
        self._restaurants = RestaurantsService()

    @method_decorator(cache_page(settings.ONE_DAY))
    def get(self, request):
        lat = request.query_params.get('lat', None)
        lng = request.query_params.get('lng', None)

        if lat == None or lng == None:
            return BAD_REQUEST({
                'Invalid request': 'Latitude and longitude are required as query parameters.'
            })

        restaurants = self._restaurants.get_within_radius(lat, lng)

        serializer = RestaurantsListResponseSerializer(restaurants, many = True)

        return Response(serializer.data)

class PrepopRestaurants(ListAPIView):
    '''
        Get prepop data from the prepop service
    '''
    permission_classes = (permissions.AllowAny,)

    def __init__(self):
        self._restaurants = RestaurantsService()
    
    @method_decorator(cache_page(settings.ONE_DAY))
    def get(self, request):
        query = request.query_params.get('q', None)

        if query == None:
            return Response([])

        prepop = self._restaurants.query_prepop(query)

        return Response(prepop)

class GetMenuItemOptions(ListAPIView):
    '''
        Get the options of a menu item. Typically called after GetMenu.
    '''
    permission_classes = (permissions.AllowAny, )

    def __init__(self):
        self._menu = MenuService()

    def get_queryset(self):
        return self._menu.get_queryset()
    
    #@method_decorator(cache_page(settings.ONE_DAY))
    def get(self, request, restaurant: str, menu_item: str):
        options = self._menu.get_options(restaurant, menu_item)

        serializer = MenuItemOptionResponseSerializer(options, many = True)

        return Response(serializer.data)

