## Import the path function from the django.urls module
## Import the RegisterView, LoginView, UserView, and LogoutView classes from the views module
from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, AssignRoleView, FetchUserRoleView, CreateCoachView, CreateAthleteView, CreateScoutView, SearchAthleteView, SearchCoachView, EditAthleteView, EditCoachView, DeleteAccountView, SendEmailView, FetchUserEmailView, FetchUserAttributesView

# Define the URL patterns for the users app
# The URL patterns all begin with http://localhost:8000/scoutbase/
# Then proceeded by the paths listed below

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('assignrole', AssignRoleView.as_view()),
    path('fetchrole', FetchUserRoleView.as_view()),
    path('coach/createprofile', CreateCoachView.as_view(), name='create_coach_profile'),
    path('athlete/createprofile', CreateAthleteView.as_view(), name='create_athlete_profile'),
    path('scout/createprofile', CreateScoutView.as_view(), name='create_scout_profile'),
    path('searchforathlete/', SearchAthleteView.as_view(), name='search_athlete'),
    path('searchforcoach/', SearchCoachView.as_view(), name='search_coach'),
    path('editcoach/<int:pk>/', EditCoachView.as_view(), name='edit_coach'),
    path('editathlete/<int:pk>/', EditAthleteView.as_view(), name='edit_athlete'),
    path('delete-account/<int:pk>/', DeleteAccountView.as_view(), name='delete_account'),
    path('send-email/', SendEmailView.as_view(), name='send_email'),
    path('fetch-email/<int:user_id>/', FetchUserEmailView.as_view(), name='fetch_user_email'),
    path('fetch-user-attributes/<int:user_id>/', FetchUserAttributesView.as_view(), name='fetch_user_attributes')
]
