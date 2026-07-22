from django.utils import timezone
from django.core.management import BaseCommand
from services.rate_limit.models import RateLimit

class Command(BaseCommand):
    help = 'Deletes expired rate limits from the database.'

    def handle(self, *args, **kwargs):
        deleted, _ = RateLimit.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()

        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} expired rate limits'))
