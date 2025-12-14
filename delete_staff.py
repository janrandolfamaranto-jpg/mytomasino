import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mytomasino.settings")
django.setup()

from user.models import StaffProfile

print("Deleting all staff profiles...")
count = 0
for profile in StaffProfile.objects.all():
    username = profile.user.username
    profile.user.delete()
    count += 1
    print(f"Deleted: {username}")

print(f"\nTotal deleted: {count}")