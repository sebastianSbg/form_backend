from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser and a predefined API token'

    def handle(self, *args, **kwargs):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        token_key = os.environ.get('API_TOKEN')

        if not username or not email or not password or not token_key:
            self.stdout.write(self.style.WARNING('Missing environment variables for superuser or token'))
            return

        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email,
            'is_superuser': True,
            'is_staff': True
        })

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created'))
        else:
            self.stdout.write(f'Superuser {username} already exists')

        token, _ = Token.objects.get_or_create(user=user)
        if token.key != token_key:
            token.delete()
            token = Token.objects.create(user=user, key=token_key)
        self.stdout.write(self.style.SUCCESS(f'Token set: {token.key}'))
