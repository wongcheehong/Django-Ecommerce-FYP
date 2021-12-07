from . import views
from django.urls import path


app_name = 'shop'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('search/', views.product_search, name='product_search'),
    path('admin/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]