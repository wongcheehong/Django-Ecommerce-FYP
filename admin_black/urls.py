from . import views
from django.urls import path

app_name = 'admin_black'

urlpatterns = [
    path('', views.index, name="index")
]