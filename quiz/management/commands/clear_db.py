from django.core.management import BaseCommand
from ...models import Quiz, Question, Option


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Deleting all data in Quiz, Question and Option tables...")

        Quiz.objects.all().delete()
        Question.objects.all().delete()
        Option.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Bulk delete operation completed!"))
