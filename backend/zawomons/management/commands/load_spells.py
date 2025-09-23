from django.core.management.base import BaseCommand
from zawomons.models import Spell

class Command(BaseCommand):
    help = 'Load spells data into the database, overwriting existing spells'

    def handle(self, *args, **options):
        SPELLS_DATA = [
            {
                'spell_id': 0,
                'name': 'Fireball2',
                'description': 'Launches a ball of fire that deals damage to enemies.',
                'spell_img': 'https://example.com/spells/fireball.png'
            },
            {
                'spell_id': 1,
                'name': 'Heal',
                'description': 'Restores health to the target.',
                'spell_img': 'https://example.com/spells/heal.png'
            },
            {
                'spell_id': 2,
                'name': 'Lightning Bolt',
                'description': 'Strikes enemies with lightning, causing area damage.',
                'spell_img': 'https://example.com/spells/lightning.png'
            },
            {
                'spell_id': 3,
                'name': 'Ice Shield',
                'description': 'Creates a protective ice barrier around the caster.',
                'spell_img': 'https://example.com/spells/ice_shield.png'
            },
            {
                'spell_id': 4,
                'name': 'Poison Cloud',
                'description': 'Creates a cloud of poisonous gas that damages over time.',
                'spell_img': 'https://example.com/spells/poison.png'
            },
            {
                'spell_id': 5,
                'name': 'Teleport',
                'description': 'Instantly moves the caster to a different location.',
                'spell_img': 'https://example.com/spells/teleport.png'
            },
            {
                'spell_id': 6,
                'name': 'Summon Wolf',
                'description': 'Summons a wolf companion to aid in battle.',
                'spell_img': 'https://example.com/spells/wolf.png'
            },
            {
                'spell_id': 7,
                'name': 'Earthquake',
                'description': 'Causes the ground to shake, stunning nearby enemies.',
                'spell_img': 'https://example.com/spells/earthquake.png'
            },
            {
                'spell_id': 8,
                'name': 'Invisibility',
                'description': 'Makes the caster temporarily invisible.',
                'spell_img': 'https://example.com/spells/invisibility.png'
            },
            {
                'spell_id': 9,
                'name': 'Time Stop',
                'description': 'Freezes time for a brief moment.',
                'spell_img': 'https://example.com/spells/time_stop.png'
            },
        ]

        self.stdout.write('Loading spells data...')

        # usuwamy wszystkie istniejące spelle
        Spell.objects.all().delete()
        self.stdout.write('Cleared existing spells')

        # dodajemy nowe spelle
        spells_created = 0
        for spell_data in SPELLS_DATA:
            spell, created = Spell.objects.update_or_create(
                spell_id=spell_data['spell_id'],
                defaults={
                    'name': spell_data['name'],
                    'description': spell_data['description'],
                    'spell_img': spell_data['spell_img']
                }
            )
            if created:
                spells_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {len(SPELLS_DATA)} spells ({spells_created} created, {len(SPELLS_DATA) - spells_created} updated)'
            )
        )