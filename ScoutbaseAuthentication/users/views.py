# Import the jwt and datetime modules from the PyJWT package
# Import the APIView class from the rest_framework.views module
# Import the UserSerializer class from the serializers module
# Import the Response class from the rest_framework.response module
# Import the User model from the models module
# Import the AuthenticationFailed exception from the rest_framework.exceptions module

import jwt
import datetime
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import UserSerializer, AthleteProfileSerializer, CoachProfileSerializer, ScoutProfileSerializer
from rest_framework.response import Response
from .models import User, AthleteProfile, CoachProfile, ScoutProfile
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .models import User, CoachProfile
from .serializers import CoachProfileSerializer


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
    
class FetchUserRoleView(APIView):
    def get(self, request):
        # Extract and validate 'user_id' from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            user_id = int(user_id)  # Ensure user_id is a valid integer
        except ValueError:
            return Response({"error": "user_id must be a number"}, status=400)

        # Fetch the user using the validated user_id
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        # Fetch the user's role
        if not user.role:
            return Response({"role": None, "message": "User has no role assigned"}, status=200)

        # Return the role information
        return Response({"role": user.role.name}, status=200)


class CreateCoachView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        if hasattr(user, 'coach_profile'):
            raise ValidationError("Coach profile already exists for this user.")

        serializer = CoachProfileSerializer(data=request.data)
        if serializer.is_valid():
            coach_profile = serializer.save(user=user)
            return Response(CoachProfileSerializer(coach_profile).data, status=201)
        return Response(serializer.errors, status=400)

class CreateAthleteView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        if hasattr(user, 'athlete_profile'):
            raise ValidationError("Athlete profile already exists for this user.")

        serializer = AthleteProfileSerializer(data=request.data)
        if serializer.is_valid():
            athlete_profile = serializer.save(user=user)
            return Response(AthleteProfileSerializer(athlete_profile).data, status=201)
        return Response(serializer.errors, status=400)


class CreateScoutView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')

        # Fetch the user by ID
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        # Check if the user already has a scout profile
        if hasattr(user, 'scout_profile'):
            raise ValidationError("Scout profile already exists for this user.")

        # Serialize the scout profile data
        serializer = ScoutProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Create the scout profile and associate it with the user
            scout_profile = serializer.save(user=user)
            return Response(ScoutProfileSerializer(scout_profile).data, status=201)
        return Response(serializer.errors, status=400)

class SearchAthleteView(ListAPIView):
    serializer_class = AthleteProfileSerializer

    def get_queryset(self):
        queryset = AthleteProfile.objects.all()
        
        # Get query parameters
        user_id = self.request.query_params.get('user_id', None)
        high_school_name = self.request.query_params.get('high_school_name', None)
        positions = self.request.query_params.get('positions', None)
        state = self.request.query_params.get('state', None)
        height = self.request.query_params.get('height', None)
        weight = self.request.query_params.get('weight', None)

        # Apply filters if parameters are provided
        if high_school_name:
            queryset = queryset.filter(high_school_name__icontains=high_school_name)
        if positions:
            queryset = queryset.filter(positions__icontains=positions)
        if state:
            queryset = queryset.filter(state__icontains=state)
        if height:
            queryset = queryset.filter(height=height)
        if weight:
            queryset = queryset.filter(weight=weight) 
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset


class SearchCoachView(ListAPIView):
    serializer_class = CoachProfileSerializer

    def get_queryset(self):
        queryset = CoachProfile.objects.all()
        
        # Get query parameters
        user_id = self.request.query_params.get('user_id', None)
        team_needs = self.request.query_params.get('team_needs', None)
        school_name = self.request.query_params.get('school_name', None)
        state = self.request.query_params.get('state', None)

        # Apply filters if parameters are provided
        if team_needs:
            queryset = queryset.filter(team_needs__icontains=team_needs)
        if school_name:
            queryset = queryset.filter(school_name__icontains=school_name)
        if state:
            queryset = queryset.filter(state__icontains=state)
        if user_id:
            queryset = queryset.filter(user_id=user_id) 

        return queryset


    

class EditCoachView(APIView):
    def put(self, request, pk):
        try:
            coach_profile = CoachProfile.objects.get(user_id=pk)  # <-- Change to user_id
        except CoachProfile.DoesNotExist:
            return Response({"error": "Coach profile not found"}, status=HTTP_404_NOT_FOUND)

        serializer = CoachProfileSerializer(coach_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class EditAthleteView(APIView):
    def put(self, request, pk):
        try:
            athlete_profile = AthleteProfile.objects.get(user_id=pk)  # <-- Change this line
        except AthleteProfile.DoesNotExist:
            return Response({"error": "Athlete profile not found"}, status=HTTP_404_NOT_FOUND)

        serializer = AthleteProfileSerializer(athlete_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
