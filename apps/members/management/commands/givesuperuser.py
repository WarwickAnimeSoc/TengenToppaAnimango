from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Gives superuser permissions to the specified user'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['usernames']:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_admin = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS('User ' + username + ' is now superuser'))
