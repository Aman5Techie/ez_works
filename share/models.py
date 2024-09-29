from django.db import models

# Create your models here.
from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        username: str = None,
        password: str = None,
        user_type: str = 'client',
        is_active: bool = True,
        **extra_fields: Any
    ) -> 'User':
        """
        Create and return a 'User' with an email, username, password, and other optional fields.
        """
        if not email:
            raise ValueError("The Email field must be set.")
        if not password:
            raise ValueError("The Password field must be set.")
        
        email = self.normalize_email(email)  # Normalize the email
        user = self.model(email=email, username=username, user_type=user_type, is_active=is_active, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)  # Save the user to the database

        return user

    def create_staff_user(self, email: str, username: str, password: str = None) -> 'User':
        """
        Create and return a staff user with an email, username, and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email: str, username: str, password: str = None) -> 'User':
        """
        Create and return a superuser with an email, username, and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client User'),
        ('operation', 'Operation User'),
    )

    # User fields
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Add is_active for user status
    is_staff = models.BooleanField(default=False)  # Allow staff users
    is_admin = models.BooleanField(default=False)  # Allow admin users

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
