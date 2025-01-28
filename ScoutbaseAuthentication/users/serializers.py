from rest_framework import serializers
from .models import User, Role, AthleteProfile, CoachProfile, ScoutProfile

# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']  # Include only necessary fields

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    # Add role as a nested serializer
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=False,
        allow_null=True
    )  # For assigning a role by ID during creation or update

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'role_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

# AthleteProfile Serializer
class AthleteProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    class Meta:
        model = AthleteProfile
        fields = ['high_school_name', 'positions', 'youtube_video_link', 'profile_picture', 'height', 'weight', 'bio', 'state']

    def validate_youtube_video_link(self, value):
        
        if value and not value.startswith('https://www.youtube.com/'):
            raise serializers.ValidationError("Invalid YouTube URL")
        return value

# CoachProfile Serializer
class CoachProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    class Meta:
        model = CoachProfile
        fields = ['team_needs', 'school_name','bio', 'profile_picture', 'state']

# ScoutProfile Serializer
class ScoutProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutProfile
        fields = ['id']  # Include at least one field or more as per your requirements
