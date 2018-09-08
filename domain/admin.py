from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(RestaurantMenuItemCategory)
admin.site.register(RestaurantMenuItem)
admin.site.register(LiqourOutletCategory)
admin.site.register(LiqourOutletMenuItem)
admin.site.register(LiqourOutletOperatingHours)
admin.site.register(AppUser)
admin.site.register(Order)
admin.site.register(OrderLineItem)
admin.site.register(Restaurant)
admin.site.register(OptionCategory)
admin.site.register(Option)
admin.site.register(RestaurantMenuItemOption)
admin.site.register(RestaurantOperatingHours)