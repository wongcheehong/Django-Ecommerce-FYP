from django.contrib import admin
from .models import Product, Category
from django.contrib import messages


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def has_delete_permission(self, request, obj=None):
        return False


def make_product_active(modeladmin, request, queryset):
    queryset.update(available=True)
    messages.success(request, "Selected Record(s) Marked as Available Successfully !!")


def make_product_inactive(modeladmin, request, queryset):
    queryset.update(available=False)
    messages.success(request, "Selected Record(s) Marked as Unavailable Successfully !!")


admin.site.disable_action('delete_selected')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'image', 'available', 'stock', 'created']
    list_filter = ['category', 'available', 'created']
    list_editable = ['price', 'available', 'stock']
    prepopulated_fields = {'slug': ('name',)}
    actions = [make_product_active, make_product_inactive]
    search_fields = ('name', 'description',)

    def delete_model(self, request, obj):
        obj.available = False
        obj.save()
