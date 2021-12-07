from django.db import models
from django.conf import settings
from shop.models import Product


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    payment_time = models.DateTimeField(blank=True, null=True)
    shipping_name = models.CharField(max_length=155)
    shipping_address = models.CharField(max_length=100)
    billing_name = models.CharField(max_length=100)
    billing_address = models.CharField(max_length=155)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    amount = models.DecimalField(decimal_places=2, max_digits=9, null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_total_item_price() for item in self.order_items.all())


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price per Unit')

    def get_total_item_price(self):
        return self.quantity*self.product.price

    def __str__(self):
        return f"{self.quantity} of {self.product}"
