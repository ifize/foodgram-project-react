from core.models import Tag
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Команда для создания тэгов в БД'

    def handle(self, *args, **kwargs):
        """
        Запуск произвести командой python manage.py import_tags
        """
        data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'dinner'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'supper'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS(
            'Импорт тегов произведен успешно!'))
