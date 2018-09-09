from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Index.as_view()),
    path('account/register/', views.Register.as_view()),
    path('restaurants/location/', views.GetWithinRadius.as_view()),
    path('restaurants/search/', views.GetRestaurants.as_view()),
    path('suggest/', views.PrepopRestaurants.as_view()),
    path('restaurants/<str:name>/menu/', views.GetMenu.as_view()),
    path('order/create/', views.CreateOrder.as_view()),
    path('orders/<int:order_id>/cancel/', views.CancelOrder.as_view()),
    path('orders/<int:order_id>/update/', views.UpdateOrder.as_view()),
    path('restaurants/<str:restaurant>/menu/<str:menu_item>/', views.GetMenuItemOptions.as_view()),
    path('admin/', include('merchants.urls')),
    path('auth/', include('oauth2_provider.urls', namespace='oauth2_provider'))
]

#from utils import menu_create

#menu_create.process()

from services.restaurants import RestaurantsService

#RestaurantsService().set_prepop()