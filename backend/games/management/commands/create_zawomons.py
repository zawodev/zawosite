from django.core.management.base import BaseCommand
from games.models import Game

class Command(BaseCommand):
    help = 'Tworzy grę Zawomons w bazie danych'

    def handle(self, *args, **options):
        game, created = Game.objects.get_or_create(
            slug='zawomons',
            defaults={
                'name': 'Zawomons',
                'description': 'Gra o zbieraniu i walce potworów',
                'unity_build_url': '/games/zawomons/',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Gra Zawomons została stworzona!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Gra Zawomons już istnieje!')
            )
        
        self.stdout.write(f'ID gry: {game.id}, Nazwa: {game.name}, Slug: {game.slug}')
