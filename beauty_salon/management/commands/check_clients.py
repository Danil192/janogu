from django.core.management.base import BaseCommand
from beauty_salon.models import Client

class Command(BaseCommand):
    help = 'Check clients in database'

    def handle(self, *args, **kwargs):
        clients = Client.objects.all()
        count = clients.count()
        
        self.stdout.write(f'Total clients: {count}')
        
        if count > 0:
            self.stdout.write('\nFirst 5 clients:')
            for client in clients[:5]:
                self.stdout.write(f'- ID: {client.id}, Name: {client.name}, User: {client.user}')
        else:
            self.stdout.write(self.style.WARNING('No clients found in database')) 