from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    alphanumeric = RegexValidator(r'^[a-zA-Z ]*$', 'Only letters are allowed.')
    first_name = models.CharField(max_length=150, blank=False, validators=[alphanumeric])
    last_name = models.CharField(max_length=150, blank=False, validators=[alphanumeric])
    email = models.EmailField(blank=False)


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='address')
    address_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=30)
    zip = models.CharField(max_length=5)
    default_shipping = models.BooleanField(default=False)
    default_billing = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.address_name}-{self.street_address}'

    class Meta:
        verbose_name_plural = 'Addresses'