from django.db import models
from django.contrib.auth.models import User

from .base.abstract import Place, OperatingHours, Category, MenuItem
from .constants import ORDER_STATUSES

# Create your models here.
class AppUser(models.Model):
    '''
        Abstract user class for the app
    '''
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    cellphone = models.CharField(max_length = 10, unique = True)
    nickname = models.CharField(max_length = 20, null = True, blank = True)
    accepted_terms = models.BooleanField(default = False)
    email_verified = models.BooleanField(default = False)
    cellphone_verified = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'appusers'

    def __str__(self):
        return self.user.username
    

class Restaurant(Place):
    '''
        Represents a restaurant
    '''
    appuser = models.ForeignKey(AppUser, on_delete = models.CASCADE, related_name = 'restaurants')
    cuisine = models.CharField(max_length = 150, db_index = True)
    capacity = models.IntegerField(default = 0, null = True, blank = True)
    class Meta:
        db_table = 'restaurants'
        ordering = ('-id',)
        unique_together = ('name', 'appuser')

class LiqourOutlet(Place):
    '''
        Represents a liqouor outlet
    '''
    appuser = models.ForeignKey(AppUser, on_delete = models.CASCADE, related_name = 'liqour_outlets')
    class Meta:
        db_table = 'liqour_outlets'
        ordering = ('-id',)
        
days = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

class RestaurantOperatingHours(OperatingHours):
    '''
        Represents a restaurant's operating hours
    '''
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = 'operating_hours')
    class Meta:
        db_table = 'restaurants_operating_hours'
        verbose_name = 'Restaurant Operating Hours'
        verbose_name_plural = 'Restaurant Operating Hours'
        unique_together = ('restaurant', 'day')

    def __str__(self):
        return f'{self.restaurant.name} - {days.get(self.day)}'  

class LiqourOutletOperatingHours(OperatingHours):
    '''
        Represents a restaurant's operating hours
    '''
    liqour_outlet = models.ForeignKey(LiqourOutlet, on_delete = models.CASCADE, related_name = 'operating_hours')
    class Meta:
        db_table = 'liqour_outlets_operating_hours'
        verbose_name = 'Liqour Outlet Operating Hours'
        verbose_name_plural = 'Liqour Outlet Operating Hours'

    def __str__(self):
        return f'{self.liqour_outlet.name} - {days.get(self.day)}'


    def __str__(self):
        return self.name

class RestaurantMenuItemCategory(Category):
    '''
        Represents the categories of a restaurant's menu. E.g. burgers, pizza etc
    '''
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE)
    class Meta:
        db_table = 'restaurants_menu_items_categories'
        unique_together = ('restaurant', 'name')
    
class LiqourOutletCategory(Category):
    '''
        Represents the categories of a liqour outlet's menu. E.g. spirits, beers, wines etc
    '''
    liqour_outlet = models.ForeignKey(LiqourOutlet, on_delete = models.CASCADE)
    class Meta:
        db_table = 'liqour_outlets_categories'
        unique_together = ('liqour_outlet', 'name')

class Drink(models.Model):
    category = models.ForeignKey(LiqourOutletCategory, on_delete = models.CASCADE)
    name = models.CharField(max_length = 50, db_index = True)
    price = models.DecimalField(max_digits = 12, decimal_places = 2, db_index = True)

    class Meta:
        ordering = ('name', 'price')
        db_table = 'drinks'

    def __str__(self):
        return self.name
    
class Order(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name = 'orders', on_delete = models.CASCADE)
    appuser = models.ForeignKey(AppUser, related_name = 'orders', on_delete = models.CASCADE)
    status = models.CharField(db_index = True, choices = ORDER_STATUSES, default = 'Submitted', max_length = 12)
    total = models.DecimalField(db_index = True, max_digits = 10, decimal_places = 2, default = 0)
    note = models.TextField(max_length = 200, blank = True)
    created_on = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'orders'
        ordering = ('-created_on',)

class OptionCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = 'option_categories')
    mandatory = models.BooleanField(default = False)
    multiple_choice = models.BooleanField(default = False)
    num_choose = models.IntegerField(default = 1)
    heading = models.CharField(max_length = 50)
    active = models.BooleanField(default = True, db_index = True)
    
    class Meta:
        db_table = 'option_categories'
        ordering = ('heading',)
        unique_together = ('restaurant', 'heading')
        verbose_name = 'Option Category'
        verbose_name_plural = 'Option Categories'

    def __str__(self):
        return self.heading

class Option(models.Model):
    category = models.ForeignKey(OptionCategory, on_delete = models.CASCADE, related_name = 'options')
    name = models.CharField(max_length = 50, db_index = True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)

    class Meta:
        db_table = 'options'
        ordering = ('name',)
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    def __str__(self):
        return self.name

class RestaurantMenuItem(MenuItem):
    category = models.ForeignKey(RestaurantMenuItemCategory, related_name = 'menu_items', on_delete = models.CASCADE)

    class Meta:
        db_table = 'restaurants_menu_items'

class LiqourOutletMenuItem(MenuItem):
    category = models.ForeignKey(LiqourOutletCategory, related_name = 'menu_items', on_delete = models.CASCADE)

    class Meta:
        db_table = 'liqour_outlets_menu_items'

class RestaurantMenuItemOption(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(RestaurantMenuItem, on_delete=models.CASCADE)
    option_category = models.ForeignKey(OptionCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = 'restaurant_menuitem_options'

class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, related_name = 'line_items', on_delete = models.CASCADE)
    menu_item = models.ForeignKey(RestaurantMenuItem, on_delete = models.CASCADE)
    unit_price = models.DecimalField(max_digits=6, decimal_places = 2)
    quantity = models.IntegerField()
    sub_total = models.DecimalField(max_digits = 10, decimal_places = 2)
    created_on = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'order_line_items'
        ordering = ('-id',)

class ChatRoom(models.Model):
    name = models.CharField(max_length = 200, db_index = True)
    created_by = models.ForeignKey(AppUser, on_delete = models.CASCADE, related_name = 'chatrooms')
    other_user = models.ForeignKey(AppUser, on_delete = models.CASCADE)
    created_on = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'chat_threads'
        ordering = ('-created_on',)

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name = 'messages', on_delete = models.CASCADE)
    message = models.CharField(max_length = 250)
    sender = models.ForeignKey(AppUser, on_delete = models.CASCADE, related_name = 'sent_messages')
    receiver = models.ForeignKey(AppUser, on_delete = models.CASCADE, related_name = 'received_messages')
    sent = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default = False)

    class Meta:
        db_table = 'chat_messages'
        ordering = ('-sent',)
