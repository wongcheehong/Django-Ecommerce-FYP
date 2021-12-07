from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'cart'

urlpatterns = [
    path('add/<int:id>/', views.cart_add, name='cart_add'),
    path('remove/<int:id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:id>/', views.cart_update, name='cart_update'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('increment/<int:id>/', views.item_increment, name='item_increment'),
    path('decrement/<int:id>/', views.item_decrement, name='item_decrement'),
    path('', views.cart_detail, name='cart_detail'),
]