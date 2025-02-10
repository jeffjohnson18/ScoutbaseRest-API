################################################################################
# Serializer Classes
# This module handles data serialization and validation for the Scoutbase platform.
# 
# Features:
# - User data serialization with role management
# - Profile serialization for Athletes, Coaches, and Scouts
# - Data validation and transformation
# - Image handling for profile pictures
################################################################################

# Django and DRF imports
from rest_framework import serializers

# Local application imports
from .models import User, Role, AthleteProfile, CoachProfile, ScoutProfile

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for user roles.
    
    Fields:
        - id: int (read-only)
        - name: string
    
    Used for role assignment and retrieval in user management.
    """
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user accounts.
    
    Fields:
        - id: int (read-only)
        - name: string
        - email: string
        - password: string (write-only)
        - role: RoleSerializer (nested, read-only)
        - role_id: int (write-only)
    
    Features:
        - Secure password handling
        - Nested role serialization
        - Role assignment via ID
    """
    # Nested serializer for role details
    role = RoleSerializer(read_only=True)
    
    # Field for role assignment during creation/update
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'role_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Creates a new user instance with hashed password.
        
        Args:
            validated_data: Dict containing user data
        
        Returns:
            User: Created user instance
        """
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Updates an existing user instance.
        
        Args:
            instance: Existing user instance
            validated_data: Dict containing updated data
        
        Returns:
            User: Updated user instance
        """
        return super().update(instance, validated_data)

class AthleteProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for athlete profiles.
    
    Fields:
        - high_school_name: string
        - positions: string
        - youtube_video_link: string (validated)
        - profile_picture: ImageField (optional)
        - height: integer
        - weight: integer
        - bio: string
        - state: string
    
    Features:
        - YouTube URL validation
        - Optional profile picture upload
        - Comprehensive athlete details
    """
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
        allow_empty_file=True
    )

    class Meta:
        model = AthleteProfile
        fields = [
            'high_school_name',
            'positions',
            'youtube_video_link',
            'profile_picture',
            'height',
            'weight',
            'bio',
            'state',
            'batting_arm',
            'throwing_arm'
        ]

    def validate_youtube_video_link(self, value):
        """
        Validates YouTube video URL format.
        
        Args:
            value: URL string to validate
        
        Returns:
            string: Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if value and not value.startswith('https://www.youtube.com/'):
            raise serializers.ValidationError("Invalid YouTube URL")
        return value

class CoachProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for coach profiles.
    
    Fields:
        - team_needs: string
        - school_name: string
        - bio: string
        - profile_picture: ImageField (optional)
        - state: string
    
    Features:
        - Optional profile picture upload
        - Team and school information
        - Coach biography
    """
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
        allow_empty_file=True
    )

    class Meta:
        model = CoachProfile
        fields = [
            'team_needs',
            'school_name',
            'bio',
            'profile_picture',
            'state'
        ]

class ScoutProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for scout profiles.
    
    Fields:
        - id: int
    
    Note:
        Minimal implementation - expand fields based on requirements.
    """
    class Meta:
        model = ScoutProfile
        fields = ['id']
