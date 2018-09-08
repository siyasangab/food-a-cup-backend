from django.urls import path, include

from . import views

urlpatterns = [
    path('restaurants/add/', views.AddRestaurant.as_view()),
    path('restaurants/<int:restaurant_id>/update/', views.UpdateRestaurant.as_view()),
    path('restaurants/<int:restaurant_id>/option-categories/', views.GetOptionCategories.as_view()),
    path('restaurants/', views.GetRestaurants.as_view()),
    path('option-categories/add/', views.AddOptionCategory.as_view()),
    path('option-categories/<int:id>/update/', views.UpdateOptionCategory.as_view()),
    path('categories/<int:id>/update/', views.UpdateCategory.as_view()),
    path('restaurants/<int:restaurant_id>/categories/add/', views.AddCategory.as_view()),
    path('orders/<int:restaurant_id>/', views.GetOrders.as_view()),
    path('orders/<int:order_id>/accept', views.AcceptOrder.as_view())
]
