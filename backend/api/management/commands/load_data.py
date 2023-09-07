from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Load data into db'

    def handle(self, *args, **options):
        import csv
        with open("/data/ingredients.csv", encoding='utf8') as f:
            reader = csv.reader(f)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]
                Ingredient(name=name, measurement_unit=measurement_unit).save()