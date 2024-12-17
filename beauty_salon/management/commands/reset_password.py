from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reset password for danil user'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='danil')
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Password reset successful'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User danil not found')) 