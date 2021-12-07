from . import views
from django.urls import path

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment_view, name='payment'),
    path('order/<int:order_id>/invoice/', views.invoice_pdf, name='invoice_pdf'),
    # Order History
    path('purchase/list/', views.my_orders, name='orders_history'),
    # Ajax request
    path('get-address-list/', views.get_address_list, name='get_address_list'),
    path('get-address/', views.get_address, name='get_address'),
    path('receive-order/', views.receive_order, name='receive_order'),
    path('cancel-order/', views.cancel_order, name='cancel_order'),
    path('buy-again/<int:order_id>/', views.buy_again, name='buy_again'),
]