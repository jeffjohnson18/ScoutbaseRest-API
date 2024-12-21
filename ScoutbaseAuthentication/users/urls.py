## Import the path function from the django.urls module
## Import the RegisterView, LoginView, UserView, and LogoutView classes from the views module
from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, AssignRoleView, FetchUserRoleView, CreateCoachView, CreateAthleteView, CreateScoutView, SearchAthleteView, SearchCoachView

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
]
