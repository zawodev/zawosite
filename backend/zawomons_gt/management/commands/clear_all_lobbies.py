from django.core.management.base import BaseCommand
from zawomons_gt.models import Lobby


class Command(BaseCommand):
    help = 'Delete ALL lobbies (use with caution!)'

    def handle(self, *args, **options):
        count = Lobby.objects.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No lobbies to delete')
            )
            return
        
        lobby_codes = list(Lobby.objects.values_list('code', flat=True))
        Lobby.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🧹 Deleted ALL {count} lobbies: {", ".join(lobby_codes)}'
            )
        )
