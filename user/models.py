from django.db import models
import random
import string
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # store hashed password
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_code(length=6):
        return ''.join(random.choices(string.digits, k=length))

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"{self.email}"
