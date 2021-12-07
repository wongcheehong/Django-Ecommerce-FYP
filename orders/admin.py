from django.contrib import admin
from .models import Order, OrderItem
from django.http import HttpResponse
import csv
import datetime


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_to_csv.short_description = 'Export to CSV'


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     def has_view_permission(self, request, obj=None):
#         return True
#
#     def has_change_permission(self, request, onj=None):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def has_add_permission(self, request,  obj=None):
#         return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ("product",)

    def has_change_permission(self, request, onj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request,  obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'paid', 'payment_time', 'created', 'shipping_name',
                       'shipping_address', 'billing_name', 'billing_address', 'received', 'cancelled', 'amount']
    list_display = ['id', 'user', 'paid', 'created', 'shipping_name', 'shipping_address', 'being_delivered', 'received']
    list_filter = ['paid', 'created', 'updated', 'being_delivered']
    inlines = [OrderItemInline]
    actions = [export_to_csv]
    fields = ['user', 'paid', 'payment_time', 'shipping_name', 'shipping_address',
              'billing_name', 'billing_address', 'being_delivered', 'received', 'cancelled', 'amount']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


