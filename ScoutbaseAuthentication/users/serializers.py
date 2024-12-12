## Importing necessary libraries
from rest_framework import serializers
from .models import User

## Creating a UserSerializer class that extends the ModelSerializer class
## The UserSerializer class is used to serialize the User model

## The UserSerializer class has the following fields:
## - id: The id field of the User model
## - name: The name field of the User model
## - email: The email field of the User model
## - password: The password field of the User model

class UserSerializer(serializers.ModelSerializer):
## The Meta class is used to define the model and fields for the UserSerializer class
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
## The create method is used to create a new user instance with the validated data
## The password field is set separately using the set_password method
## The user instance is saved and returned

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

