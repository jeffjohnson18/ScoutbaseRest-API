# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager

# Custom UserManager to handle user creation without username
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Custom User model
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None  # Disable default username field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True,
    )

    role = models.ForeignKey(
        "Role", on_delete=models.SET_NULL, null=True, blank=True, related_name="users",
    )

    objects = UserManager()

    def __str__(self):
        return self.email

# Role model
class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(
        Permission, related_name="role_permissions", blank=True,
    )

    def __str__(self):
        return self.name

# AthleteProfile model
class AthleteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_profile')
    high_school_name = models.CharField(max_length=255, default="Unknown")
    positions = models.CharField(max_length=255, default="Unknown")
    youtube_video_link = models.URLField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    height = models.FloatField(default=6.0)
    weight = models.IntegerField(default=150)
    bio = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=255, default="Unknown")

# CoachProfile model
class CoachProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    team_needs = models.CharField(max_length=255, default="None")
    school_name = models.CharField(max_length=255, default="Unknown")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    state = models.CharField(max_length=100, default="Unknown")

# ScoutProfile model
class ScoutProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="scout_profile")

    def __str__(self):
        return self.user.email