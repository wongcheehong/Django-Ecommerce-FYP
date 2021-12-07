from .models import Profile
from django.core.exceptions import ObjectDoesNotExist


def save_profile(backend, user, response, *args, **kwargs):
    try:
        user.profile
    except ObjectDoesNotExist:
        Profile.objects.create(user=user)
