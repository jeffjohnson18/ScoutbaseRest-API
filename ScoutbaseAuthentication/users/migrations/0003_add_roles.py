from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Role.objects.get_or_create(name="Athlete")
    Role.objects.get_or_create(name="Coach")
    Role.objects.get_or_create(name="Scout")

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers_athleteprofile_coachprofile_and_more'),  # Replace with your last migration name
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
