from django.apps import AppConfig

## This is the configuration file for the users app
## It is used to define the default auto field and the name of the app
## The name of the app is used to refer to it in other parts of the project
## The default auto field is used to define the primary key field type
## In this case, the primary key field type is BigAutoField
class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
