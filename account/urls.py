from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='user_edit'),

    # Address Book
    path('create-address/', views.address_create, name='address_create'),
    path('update-address/', views.update_address, name='update_address'),
    path('delete-address/', views.delete_address, name='delete_address'),
    path('address-book/', views.address_book, name='address_book'),
    path('address-book/change-shipping/', views.change_shipping_default, name='change_shipping_default'),
    path('address-book/change-billing/', views.change_billing_default, name='change_billing_default'),

    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
