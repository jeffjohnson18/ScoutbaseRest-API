# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager

# Custom UserManager to handle user creation without username
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
    def get_user_role(self, user_id):
            """
            Fetch and return the role name of a user by their ID.
            """
            try:
                user = self.get(pk=user_id)
                return user.role.name if user.role else None
            except User.DoesNotExist:
                return None


# Custom User model
class User(AbstractUser):
    # Custom fields
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)  # EmailField instead of CharField for validation
    password = models.CharField(max_length=255)
    username = None  # Disables default username field

    # Specify that the email field is used for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Removes username requirement

    # Many-to-many relationships with Group and Permission
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    # Relationship with the Role model
    role = models.ForeignKey(
        "Role",
        on_delete=models.SET_NULL,  # If role is deleted, set role to null
        null=True,
        blank=True,
        related_name="users",
        help_text="The role assigned to this user.",
    )

    objects = UserManager()  # Set the custom manager here

    def __str__(self):
        return self.email


# Role model to define different roles like Coach, Player, or Scout
class Role(models.Model):
    # Role name
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the role, e.g., Coach, Player, or Scout.",
    )

    # Permissions associated with the role
    permissions = models.ManyToManyField(
        Permission,
        related_name="role_permissions",
        blank=True,
        help_text="Specific permissions for this role.",
        verbose_name="role permissions",
    )

    def __str__(self):
        return self.name

