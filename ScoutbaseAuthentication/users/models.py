# Import the models module from the django.db package
# Import the AbstractUser, Group, and Permission classes from the django.contrib.auth.models module
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# The custom user model has the following fields:

# - name: A CharField with a maximum length of 255 characters
# - email: A CharField with a maximum length of 255 characters and unique constraint
# - password: A CharField with a maximum length of 255 characters
# - username: None (to disable the default username field)
# - groups: A ManyToManyField relationship with the Group model

# Create a custom user model that extends the AbstractUser class
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

# - groups function will later be used to assign the user to a role (Coach, Player, etc)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

# - user_permissions: A ManyToManyField relationship with the Permission model

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )