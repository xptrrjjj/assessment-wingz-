from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from modules.accounts.managers import UserManager


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    DRIVER = "driver", "Driver"
    RIDER = "rider", "Rider"


class User(AbstractBaseUser, PermissionsMixin):
    id_user = models.AutoField(primary_key=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.RIDER)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [
            models.Index(fields=["email"], name="idx_user_email"),
            models.Index(fields=["role"], name="idx_user_role"),
        ]

    def __str__(self):
        return self.email
