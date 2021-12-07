from django.contrib import admin
from .models import Address, Profile


# @admin.register(Profile)
# class Profile(admin.ModelAdmin):
#     list_display = ['user', 'photo',]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request,  obj=None):
        return False
