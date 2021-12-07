from django.db import models
from django.conf import settings
from shop.models import Product


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)

    def get_total_price(self):
        return sum([cart_item.sub_total() for cart_item in self.cart_item.all()])

    def __str__(self):
        return f"{ self.user.username }\'s cart"


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey(Cart, related_name='cart_item', on_delete=models.CASCADE)

    def sub_total(self):
        return round(self.product.price * self.quantity, 2)

    def __str__(self):
        return f"{self.quantity} {self.product.name}"
