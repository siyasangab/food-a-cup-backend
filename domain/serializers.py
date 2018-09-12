from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import CharField, EmailField
from domain.models import *

class AppUserCreateSerializer(serializers.ModelSerializer):
    '''
        Serializes the appuser model
    '''
    first_name = serializers.CharField(source = 'user.first_name')
    last_name = serializers.CharField(source = 'user.last_name')
    email = serializers.EmailField(source = 'user.email')
    password = serializers.CharField(source = 'user.password')
    class Meta:
        model = AppUser
        fields = ('cellphone', 'accepted_terms', 'first_name', 'last_name', 'email', 'password')

class AppUserUpdateSerializer(serializers.ModelSerializer):
    '''
        Appuser update serializer
    '''
    class Meta:
        model = AppUser
        fields = ('nickname',)

class AppUserResponseSerializer(serializers.ModelSerializer):
    '''
        Serializes the appuser model for api responses
    '''
    first_name = serializers.CharField(source = 'user.first_name')
    last_name = serializers.CharField(source = 'user.last_name')
    email = serializers.EmailField(source = 'user.email')
    class Meta:
        model = AppUser
        fields = ('cellphone', 'first_name', 'last_name', 'email', 'nickname')

class OrderLineItemResponseSerializer(serializers.ModelSerializer):
    '''
        Order line_items response serializer, used to serialize order line_items for api responses
    '''
    menu_item_name = serializers.CharField(source = 'menu_item.name')
    class Meta:
        model = OrderLineItem
        fields = ('menu_item_name', 'unit_price', 'quantity', 'sub_total')

class OrderLineItemCreateSerializer(serializers.ModelSerializer):
    '''
        Order detail create serializer to serialize incoming order line_items on order creation
    '''
    class Meta:
        model = OrderLineItem
        fields = ('menu_item', 'quantity')

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id',)

class OrderCreateSerializer(serializers.ModelSerializer):
    '''
        Order creation serializer
    '''
    line_items = OrderLineItemCreateSerializer(many = True, required = True)
    extras = OptionSerializer(many = True)
    class Meta:
        model = Order
        fields = ('restaurant', 'note', 'line_items', 'extras')
    
    def validate(self, attrs):
        line_items = attrs.get('line_items')
        if not line_items:
            raise serializers.ValidationError({
                'line items': 'Order line items are required.'
            })
        return super().validate(attrs)

class OrderResponseSerializer(serializers.ModelSerializer):
    '''
        Order response serializer to return order responses
    '''
    customer = serializers.CharField(source = 'appuser.user.username')
    restaurant = serializers.CharField(source = 'restaurant.name')
    line_items = OrderLineItemResponseSerializer(many = True)
    class Meta:
        model = Order
        fields = ('id', 'customer', 'restaurant', 'status', 'total', 'created_on', 'last_updated', 'line_items' )

class MenuItemsResponseSerializer(serializers.ModelSerializer):
    '''
        Menu item response serializer to serialize menu item responses
    '''
    class Meta:
        model = RestaurantMenuItem
        fields = ('id', 'name', 'price', 'slug')

class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemsResponseSerializer(many = True, source = 'menu_items')
    class Meta:
        model = Category
        fields = ('name', 'items')

class RestaurantCreateSerializer(serializers.ModelSerializer):
    '''
        Restaurant create serializer to serialize restaurant create requests
    '''
    class Meta:
        model = Restaurant
        fields = ('name', 'address_line1', 'address_line2', 'suburb', 'city', 'tagline', 'capacity')
        extra_kwargs = {
            'address_line2': {
                'required': False
            },
            'tagline': {
                'required': False
            },
            'capacity': {
                'required': False
            }
        }

class RestaurantsListResponseSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        exclude = ('appuser', 'last_updated', 'created_on', 'slug')

class RestaurantsListResponseSerializer(serializers.ModelSerializer):
    '''
        Restaurants list response serializer to serialize restaurant responses
    '''
    times = serializers.SerializerMethodField('get_closing_time')
    distance = serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = ('name', 'slug', 'banner_url', 'cuisine', 'times', 'distance')

    def get_closing_time(self, obj):
        return obj.operating_hours.all()[0].closes

    def get_distance(self, obj):
        return obj.distance / 1000

class RestaurantCategoryResponseSerializer(serializers.ModelSerializer):
    '''
        Restaurant category response serialize used for serializing a restaurant's menu item categories with corresponding menu items.
        Serializes menu categories with items in one shot
    '''

    items = MenuItemsResponseSerializer(many = True, source = 'menu_items')
    class Meta:
        model = RestaurantMenuItemCategory
        fields = ('name', 'slug', 'items')

class OptionResponseSerializer(serializers.ModelSerializer):
    '''
        Options response serializer used for  serializing menu item options
    '''
    class Meta:
        model = Option
        fields = ('id', 'name', 'price')

class OptionCategoryCreateSerializer(serializers.ModelSerializer):
    '''
        Option category create serializer for serializing option category create requests
    '''
    class Meta:
        model = OptionCategory
        fields = ('heading', 'restaurant')

class OptionCategoryUpdateSerializer(serializers.ModelSerializer):
    '''
        Option category update serializer for serializing option category update requests
    '''
    class Meta:
        model = OptionCategory
        fields = ('heading', 'active')

class OptionCategoryListSerializer(serializers.ModelSerializer):
    '''
        Option category list serializer for serializing option category list responses
    '''
    options = OptionResponseSerializer(many = True)
    class Meta:
        model = OptionCategory
        fields = ('heading', 'active', 'mandatory', 'multiple_choice', 'options', 'num_choose')

class MenuItemOptionResponseSerializer(serializers.ModelSerializer):
    '''
        Menu item options response serializer is for serializing menu item options responses
    '''
    options = OptionResponseSerializer(many = True, source = 'option_category.options')
    heading = serializers.CharField(source = 'option_category.heading')
    mandatory = serializers.BooleanField(source = 'option_category.mandatory')
    multi = serializers.BooleanField(source = 'option_category.multiple_choice')
    num_choose = serializers.IntegerField(source = 'option_category.num_choose')
    class Meta:
        model = OptionCategory
        fields = ('heading', 'options', 'multi', 'mandatory', 'num_choose')

class MenuItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('name', 'price', 'category')

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'restaurant')

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


