from django.core.management.base import BaseCommand
from games.models import Game

class Command(BaseCommand):
    help = 'Tworzy grę Cleaning Time! w bazie danych'

    def handle(self, *args, **options):
        game, created = Game.objects.get_or_create(
            slug='cleaning-time',
            defaults={
                'name': 'Cleaning Time!',
                'description': 'Sprzątaj i organizuj w tej wciągającej grze single player!',
                'unity_build_url': '/games/cleaning-time/',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Gra Cleaning Time! została stworzona!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Gra Cleaning Time! już istnieje!')
            )
        
        self.stdout.write(f'ID gry: {game.id}, Nazwa: {game.name}, Slug: {game.slug}')
