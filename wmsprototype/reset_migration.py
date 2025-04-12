import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wmsprototype.settings")
django.setup()

# Now you can import Django models
from django.db import connection

def reset_statuses_migration():
    # Clear existing status records
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM wmsprototype_status")
        print("Deleted existing status records")
        
        # Remove the migration record
        cursor.execute("DELETE FROM django_migrations WHERE app='wmsprototype' AND name='0005_statuses'")
        print("Removed migration record for 0005_statuses")
        
    print("Done! Now run 'python manage.py migrate' to reapply the migration")

if __name__ == "__main__":
    reset_statuses_migration()
