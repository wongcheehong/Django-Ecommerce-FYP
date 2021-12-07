from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import path
from django.http import JsonResponse
from account.models import User, Profile
from django.contrib.auth.admin import UserAdmin
from django.views.decorators.csrf import csrf_exempt
from admin_black.models import AdminBlackSetting


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['username', 'password', 'first_name', 'last_name', 'email', 'date_joined', 'last_login']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser',),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()
        # Object is added
        if change is False:
            Profile.objects.create(user=obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'password', 'first_name', 'last_name', 'email', 'date_joined', 'last_login']
        else:
            return []

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = [
                   path('admin_black-setting/', self.admin_site.admin_view(self.setting), name='admin_black_setting'),
               ] + super().get_urls()
        return urls

    @csrf_exempt
    def setting(self, request):
        user = request.user
        if request.method == 'POST':
            params = {}

            sidebar_background = request.POST.get('sidebar_background', None)
            if sidebar_background:
                params['sidebar_background'] = sidebar_background

            dark_mode = request.POST.get('dark_mode', None)
            if dark_mode:
                params['dark_mode'] = bool(int(dark_mode))

            AdminBlackSetting.objects.update_or_create(user=user, defaults=params)

        return JsonResponse({'valid': True})


# admin.site.register(User, CustomUserAdmin)
