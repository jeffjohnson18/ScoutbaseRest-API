################################################################################
# Authentication and Profile Management Views
# This module handles user authentication, registration, profile management,
# and search functionality for the Scoutbase platform.
# 
# Features:
# - User authentication with JWT
# - Profile management for Athletes, Coaches, and Scouts
# - Role-based access control
# - Profile search functionality
################################################################################

# Standard library imports
import jwt
import datetime
import logging

# Django and DRF imports
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

# Local application imports
from .serializers import (
    UserSerializer, 
    AthleteProfileSerializer, 
    CoachProfileSerializer, 
    ScoutProfileSerializer
)
from .models import (
    User, 
    AthleteProfile, 
    CoachProfile, 
    ScoutProfile,
    Role
)

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    """
    Handles user registration.
    
    Endpoints:
        POST /register/: Creates a new user account
    
    Request Body:
        - email: string
        - password: string
        - [additional fields based on UserSerializer]
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    """
    Handles user authentication and JWT token generation.
    
    Endpoints:
        POST /login/: Authenticates user and returns JWT token
    
    Request Body:
        - email: string
        - password: string
    
    Returns:
        - JWT token in both cookie and response body
        - Token expires in 60 minutes
    """
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        # Authenticate user
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid password')
        
        # Generate JWT token
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Set token in cookie and response
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        return response

class UserView(APIView):
    """
    Retrieves user details from JWT token.
    
    Endpoints:
        GET /user/: Returns authenticated user's details
    
    Authentication:
        - Requires valid JWT token in cookies
    """
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

class LogoutView(APIView):
    """
    Handles user logout by removing JWT token.
    
    Endpoints:
        POST /logout/: Removes JWT token cookie
    """
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return response

class AssignRoleView(APIView):
    """
    Assigns roles to users.
    
    Endpoints:
        POST /assign-role/: Assigns a role to a specific user
    
    Request Body:
        - user_id: int
        - role_name: string
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        role_name = request.data.get('role_name')

        # Validate request data
        if not user_id or not role_name:
            return Response({"error": "user_id and role_name are required"}, status=400)

        # Fetch and validate user and role
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        role = Role.objects.filter(name=role_name).first()
        if not role:
            return Response({"error": f"Role '{role_name}' does not exist"}, status=404)

        # Assign role and save
        user.role = role
        user.save()
        return Response({"message": f"Role '{role_name}' assigned to user '{user.email}'"}, status=200)

class FetchUserRoleView(APIView):
    """
    Retrieves user's assigned role.
    
    Endpoints:
        GET /user-role/?user_id=<id>: Returns user's role information
    
    Query Parameters:
        - user_id: int
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            user_id = int(user_id)
        except ValueError:
            return Response({"error": "user_id must be a number"}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        if not user.role:
            return Response({"role": None, "message": "User has no role assigned"}, status=200)

        return Response({"role": user.role.name}, status=200)

class CreateCoachView(APIView):
    """
    Creates a coach profile for a user.
    
    Endpoints:
        POST /create-coach/: Creates a new coach profile
    
    Request Body:
        - user_id: int
        - profile_picture: file (optional)
        - team_needs: string (optional)
        - school_name: string (optional)
        - state: string (optional)
        - position_within_org: string (optional)
    """
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
    """
    Creates an athlete profile for a user.
    
    Endpoints:
        POST /create-athlete/: Creates a new athlete profile
    
    Request Body:
        - user_id: int
        - profile_picture: file (optional)
        - [additional athlete profile fields]
    """
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
    """
    Creates a scout profile for a user.
    
    Endpoints:
        POST /create-scout/: Creates a new scout profile
    
    Request Body:
        - user_id: int
        - [additional scout profile fields]
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        
        if not user:
            return Response({"error": "User not found"}, status=404)
        if hasattr(user, 'scout_profile'):
            raise ValidationError("Scout profile already exists for this user.")

        serializer = ScoutProfileSerializer(data=request.data)
        if serializer.is_valid():
            scout_profile = serializer.save(user=user)
            return Response(ScoutProfileSerializer(scout_profile).data, status=201)
        return Response(serializer.errors, status=400)

class SearchAthleteView(ListAPIView):
    """
    Provides filtered search functionality for athlete profiles.
    
    Endpoints:
        GET /search-athletes/: Returns filtered list of athlete profiles
    
    Query Parameters:
        - user_id: int (optional)
        - high_school_name: string (optional)
        - positions: string (optional)
        - state: string (optional)
        - height: int (optional)
        - weight: int (optional)
    """
    serializer_class = AthleteProfileSerializer

    def get_queryset(self):
        queryset = AthleteProfile.objects.all()
        
        # Apply filters based on query parameters
        filters = {
            'user_id': self.request.query_params.get('user_id'),
            'high_school_name__icontains': self.request.query_params.get('high_school_name'),
            'positions__icontains': self.request.query_params.get('positions'),
            'state__icontains': self.request.query_params.get('state'),
            'height': self.request.query_params.get('height'),
            'weight': self.request.query_params.get('weight'),
            'batting_arm': self.request.query_params.get('batting_arm'),
            'throwing_arm': self.request.query_params.get('throwing_arm')
        }
        
        # Apply non-null filters
        return queryset.filter(**{k: v for k, v in filters.items() if v is not None})

class SearchCoachView(ListAPIView):
    """
    Provides filtered search functionality for coach profiles.
    
    Endpoints:
        GET /search-coaches/: Returns filtered list of coach profiles
    
    Query Parameters:
        - user_id: int (optional)
        - team_needs: string (optional)
        - school_name: string (optional)
        - state: string (optional)
    """
    serializer_class = CoachProfileSerializer

    def get_queryset(self):
        queryset = CoachProfile.objects.all()
        
        # Apply filters based on query parameters
        filters = {
            'user_id': self.request.query_params.get('user_id'),
            'team_needs__icontains': self.request.query_params.get('team_needs'),
            'school_name__icontains': self.request.query_params.get('school_name'),
            'state__icontains': self.request.query_params.get('state')
        }
        
        # Apply non-null filters
        return queryset.filter(**{k: v for k, v in filters.items() if v is not None})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # The user_id will now be included in the serialized data
        return Response(serializer.data)

class EditCoachView(APIView):
    """
    Updates coach profile information.
    
    Endpoints:
        PUT /edit-coach/<user_id>/: Updates coach profile for specified user
    
    Path Parameters:
        - user_id: int
    """
    def put(self, request, pk):
        try:
            coach_profile = CoachProfile.objects.get(user_id=pk)
        except CoachProfile.DoesNotExist:
            return Response({"error": "Coach profile not found"}, status=HTTP_404_NOT_FOUND)

        serializer = CoachProfileSerializer(coach_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class EditAthleteView(APIView):
    """
    Updates athlete profile information.
    
    Endpoints:
        PUT /edit-athlete/<user_id>/: Updates athlete profile for specified user
    
    Path Parameters:
        - user_id: int
    """
    def put(self, request, pk):
        try:
            athlete_profile = AthleteProfile.objects.get(user_id=pk)
        except AthleteProfile.DoesNotExist:
            return Response({"error": "Athlete profile not found"}, status=HTTP_404_NOT_FOUND)

        serializer = AthleteProfileSerializer(athlete_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    """
    Handles permanent deletion of user accounts and associated profiles.
    
    Endpoints:
        DELETE /delete-account/: Permanently removes user account and related data
    
    Authentication:
        - Requires valid JWT token
    
    Security:
        - Verifies user ownership via JWT token
        - Cascading deletion of all associated profiles
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # Verify authentication
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        # Delete user and associated profiles
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)

        # Cascade delete all profiles
        AthleteProfile.objects.filter(user=user).delete()
        CoachProfile.objects.filter(user=user).delete()
        ScoutProfile.objects.filter(user=user).delete()
        user.delete()

        response = Response({"message": "Account deleted successfully"}, status=HTTP_200_OK)
        response.delete_cookie('jwt')
        return response

class SendEmailView(APIView):
    """
    Sends an email to a specified user.
    
    Endpoints:
        POST /send-email/: Sends email to specified user
    
    Request Body:
        - recipient_id: int
        - subject: string
        - message: string
    """
    
    def post(self, request):
        # Get recipient
        recipient_id = request.data.get('recipient_id')
        if not recipient_id:
            return Response({"error": "recipient_id is required"}, status=HTTP_400_BAD_REQUEST)

        recipient = User.objects.filter(id=recipient_id).first()
        if not recipient:
            return Response({"error": "Recipient not found"}, status=HTTP_404_NOT_FOUND)

        # Get email content
        subject = request.data.get('subject', 'Message from Scoutbase')
        message = request.data.get('message')
        if not message:
            return Response({"error": "message is required"}, status=HTTP_400_BAD_REQUEST)

        try:
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            return Response({
                "message": "Email sent successfully",
                "to": recipient.email
            }, status=HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Failed to send email",
                "details": str(e)
            }, status=HTTP_400_BAD_REQUEST)

class FetchUserEmailView(APIView):
    """
    Retrieves the email of a specified user.
    
    Endpoints:
        GET /fetch-email/<user_id>/: Returns the user's email information
    
    Path Parameters:
        - user_id: int
    """
    
    def get(self, request, user_id):
        # Fetch the user by ID
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)

        return Response({"email": user.email}, status=HTTP_200_OK)

class FetchUserAttributesView(APIView):
    """
    Retrieves attributes of a specified user by user ID.
    
    Endpoints:
        GET /fetch-user-attributes/<user_id>/: Returns the user's attributes
    
    Path Parameters:
        - user_id: int
    """
    
    def get(self, request, user_id):
        # Fetch the user by ID
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)

        # Prepare the user attributes to return
        user_attributes = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None,  # Assuming role is a ForeignKey
            # Add any other attributes you want to return
        }

        return Response(user_attributes, status=HTTP_200_OK)

