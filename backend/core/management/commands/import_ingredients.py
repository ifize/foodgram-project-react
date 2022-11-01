import csv
from pathlib import Path

from django.core.management import BaseCommand

from core.models import Ingredient
from foodgram.settings import BASE_DIR

PROJECT_DIR = Path(BASE_DIR).resolve().joinpath('data')
FILE_TO_OPEN = PROJECT_DIR / "ingredients.csv"


class Command(BaseCommand):
    help = 'Команда для распаковки ингредиентов в базу'

    def handle(self, *args, **options):
        with open(FILE_TO_OPEN, encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
        print('Все ингридиенты загружены.')
