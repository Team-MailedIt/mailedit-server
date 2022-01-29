from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractUser):
    LOGIN_TYPE_CHOICES = (
        ("NULL", "NULL"),
        ("GOOGLE", "GOOGLE"),
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False,
        null=False,
        error_messages={
            "unique": _("사용자의 이메일 주소가 이미 존재합니다."),
        },
    )

    login_type = models.CharField(
        max_length=10,
        default="NULL",
        choices=LOGIN_TYPE_CHOICES,
    )

    tooltip = models.BooleanField(null=False, default=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
