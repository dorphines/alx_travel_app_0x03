from django.core.management.base import BaseCommand
from listings.models import Listing
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create a user
        user, created = User.objects.get_or_create(username='testuser')
        if created:
            user.set_password('password')
            user.save()

        # Create some listings
        Listing.objects.all().delete() # Clear existing listings
        
        listings = [
            {
                'title': 'Cozy Apartment in New York',
                'description': 'A beautiful and cozy apartment in the heart of New York City.',
                'price': 150.00,
                'address': '123 Main St',
                'country': 'USA',
                'city': 'New York'
            },
            {
                'title': 'Modern Loft in London',
                'description': 'A stylish and modern loft with a great view of the city.',
                'price': 200.00,
                'address': '456 High St',
                'country': 'UK',
                'city': 'London'
            },
            {
                'title': 'Charming Villa in Tuscany',
                'description': 'A charming villa in the beautiful countryside of Tuscany.',
                'price': 300.00,
                'address': '789 Wine Rd',
                'country': 'Italy',
                'city': 'Florence'
            }
        ]

        for listing_data in listings:
            Listing.objects.create(**listing_data)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
