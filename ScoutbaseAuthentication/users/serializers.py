from rest_framework import serializers
from .models import User, Role, AthleteProfile, CoachProfile, ScoutProfile


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']  # Include only necessary fields

class UserSerializer(serializers.ModelSerializer):
    # Add role as a nested serializer
    role = RoleSerializer(read_only=True)  # Read-only for display purposes
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=False,
        allow_null=True
    )  # For assigning a role by ID during creation or update

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'role_id']  # Include role fields
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role_data = validated_data.pop('role', None)  # Remove role info for processing
        user = User.objects.create_user(**validated_data)

        if role_data:
            user.role = role_data
            user.save()

        return user

    def update(self, instance, validated_data):
        role_data = validated_data.pop('role', None)
        instance = super().update(instance, validated_data)

        if role_data:
            instance.role = role_data
            instance.save()

        return instance

# serializers.py
from rest_framework import serializers
from .models import AthleteProfile, CoachProfile, ScoutProfile

class AthleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteProfile
        fields = ['high_school_name', 'positions', 'youtube_video_link', 'profile_picture', 'height', 'weight', 'bio']

class CoachProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachProfile
        fields = ['team_needs', 'school_name', 'position', 'bio', 'profile_picture']

class ScoutProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutProfile
        fields = []  # Add specific fields for Scout profile as needed
