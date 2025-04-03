################################################################################
# Database Models
# This module defines the core data models for the Scoutbase platform.
# 
# Features:
# - Custom user model with email authentication
# - Role-based access control
# - Profile models for Athletes, Coaches, and Scouts
# - Image handling for profile pictures
################################################################################

# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    
    Replaces Django's default username-based authentication with email-based system.
    Handles user creation and superuser creation with appropriate validation.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user.
        
        Args:
            email: User's email address (required)
            password: User's password (optional)
            **extra_fields: Additional fields for User model
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email is not provided
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
        Creates and saves a new superuser.
        
        Args:
            email: Superuser's email address
            password: Superuser's password
            **extra_fields: Additional fields for User model
            
        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model using email as the unique identifier.
    
    Attributes:
        name (CharField): User's full name
        email (EmailField): User's email address (unique)
        password (CharField): Encrypted password
        role (ForeignKey): User's role in the system
        groups (ManyToManyField): Django auth groups
        user_permissions (ManyToManyField): Django auth permissions
    
    Note:
        - Username field is disabled in favor of email
        - Custom user manager handles user creation
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None  # Disable username field

    # Authentication settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Role and permissions
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user."
    )
    role = models.ForeignKey(
        "Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text="User's role in the system"
    )

    # Use custom manager
    objects = UserManager()

    def __str__(self):
        """String representation of user"""
        return self.email

class Role(models.Model):
    """
    Role model for role-based access control.
    
    Attributes:
        name (CharField): Unique role name
        permissions (ManyToManyField): Associated permissions
    
    Used to group permissions and assign them to users collectively.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique name of the role"
    )
    permissions = models.ManyToManyField(
        Permission,
        related_name="role_permissions",
        blank=True,
        help_text="Permissions associated with this role"
    )

    def __str__(self):
        """String representation of role"""
        return self.name

class AthleteProfile(models.Model):
    """
    Profile model for student athletes.
    
    Attributes:
        user (OneToOneField): Associated user account
        high_school_name (CharField): Athlete's school
        positions (CharField): Sports positions played
        youtube_video_link (URLField): Link to highlight reel
        profile_picture (ImageField): Athlete's photo
        height (FloatField): Height in feet
        weight (IntegerField): Weight in pounds
        bio (TextField): Athlete's biography
        state (CharField): State of residence/school
    
    Used to store athlete-specific information and media.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='athlete_profile',
        help_text="User account associated with this profile"
    )
    high_school_name = models.CharField(
        max_length=255,
        default="Unknown",
        help_text="Name of athlete's high school"
    )
    positions = models.CharField(
        max_length=255,
        default="Unknown",
        help_text="Sports positions played by athlete"
    )
    youtube_video_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link to athlete's highlight reel"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="Athlete's profile picture"
    )
    height = models.FloatField(
        default=6.0,
        help_text="Height in feet"
    )
    weight = models.IntegerField(
        default=150,
        help_text="Weight in pounds"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Athlete's biography"
    )
    state = models.CharField(
        max_length=255,
        default="Unknown",
        help_text="State of residence/school"
    )
    throwing_arm = models.CharField(
        max_length=255,
        default="Unknown",
        help_text="State of residence/school"
    )
    batting_arm = models.CharField(
        max_length=255,
        default="Unknown",
        help_text="State of residence/school"
    )


class CoachProfile(models.Model):
    """
    Profile model for coaches.
    
    Attributes:
        user (OneToOneField): Associated user account
        team_needs (CharField): Current team recruitment needs
        school_name (CharField): Coach's school/institution
        bio (TextField): Coach's biography
        profile_picture (ImageField): Coach's photo
        state (CharField): State of school/institution
        position_within_org (CharField): Position of the coach within the organization
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='coach_profile',
        help_text="User account associated with this profile"
    )
    team_needs = models.CharField(
        max_length=255,
        default="None",
        help_text="Current team recruitment needs"
    )
    school_name = models.CharField(
        max_length=255,
        default="Unknown",
        help_text="Name of coach's school/institution"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Coach's biography"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="Coach's profile picture"
    )
    state = models.CharField(
        max_length=100,
        default="Unknown",
        help_text="State of school/institution"
    )
    position_within_org = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Position of the coach within the organization"
    )

    def __str__(self):
        """String representation of coach profile"""
        return self.user.email

class ScoutProfile(models.Model):
    """
    Profile model for scouts.
    
    Attributes:
        user (OneToOneField): Associated user account
    
    Note:
        Minimal implementation - expand attributes based on requirements.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="scout_profile",
        help_text="User account associated with this profile"
    )

    def __str__(self):
        """String representation of scout profile"""
        return self.user.email