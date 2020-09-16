import configurations
from django.db import connection

configurations.setup()

fix_migration_state_query = (
    "UPDATE django_migrations "
    "SET app='lti_toolbox'"
    "WHERE app='lti_provider' AND name='0001_initial'"
)

with connection.cursor() as cursor:
    cursor.execute(fix_migration_state_query)
