# Import the jwt and datetime modules from the PyJWT package
# Import the APIView class from the rest_framework.views module
# Import the UserSerializer class from the serializers module
# Import the Response class from the rest_framework.response module
# Import the User model from the models module
# Import the AuthenticationFailed exception from the rest_framework.exceptions module

import jwt
import datetime
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
from rest_framework.exceptions import AuthenticationFailed

# Create a RegisterView class that extends the APIView class
# The RegisterView class is used to register a new user
# The post method is used to create a new user instance with the serialized data
# The user instance is saved and the serialized data is returned

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# Create a LoginView class that extends the APIView class
# The LoginView class is used to log in a user
# The post method is used to authenticate the user with the provided email and password
# If the user is not found, an AuthenticationFailed exception is raised
# If the password is invalid, an AuthenticationFailed exception is raised
# A payload is created with the user id, expiration time, and issue time
# The payload is encoded into a JWT token
# The token is set as a cookie in the response
# The token is returned in the response data

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid password')
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {
            'jwt': token
        }

        return response

# Create a UserView class that extends the APIView class
# The UserView class is used to get the user details from a session (token)
# The get method is used to get the JWT token from the request cookies
# If the token is not found, an AuthenticationFailed exception is raised
# The token is decoded to get the payload
# If the token is expired, an AuthenticationFailed exception is raised
# The user is fetched from the database using the user id from the payload
# The user is serialized and returned in the response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')
        
        try: 
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        
        return Response(token)
    
# Create a LogoutView class that extends the APIView class
# The LogoutView class is used to log out a user
# The post method is used to delete the JWT token from the response cookies
# A success message is returned in the response data

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
    
    # Import the Role model
from .models import Role

# Add a new APIView for assigning roles
class AssignRoleView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        role_name = request.data.get('role_name')

        if not user_id or not role_name:
            return Response({"error": "user_id and role_name are required"}, status=400)

        # Fetch the user by ID
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        # Fetch the role by name
        role = Role.objects.filter(name=role_name).first()
        if not role:
            return Response({"error": f"Role '{role_name}' does not exist"}, status=404)

        # Assign the role to the user
        user.role = role
        user.save()

        return Response({"message": f"Role '{role_name}' assigned to user '{user.email}'"}, status=200)
