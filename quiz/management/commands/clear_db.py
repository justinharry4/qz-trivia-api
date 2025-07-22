import logging

from django.core.management import BaseCommand
from django.db import transaction

from ...models import Quiz, Question, Option


logger = logging.getLogger(__name__)


class Command(BaseCommand):
	def handle(self, *args, **options):
		logger.info('Quiz data clearing operation started')
		self.stdout.write("Deleting all data in Quiz, Question and Option tables...")

		try:
			with transaction.atomic():
				Quiz.objects.all().delete()
				Question.objects.all().delete()
				Option.objects.all().delete()

				logger.info('Quiz data cleared from database successfully')
				self.stdout.write(self.style.SUCCESS("Bulk delete operation completed!"))
		except Exception:
			logger.error('Quiz data clearing operation failed', exc_info=True)
			self.stdout.write(self.style.ERROR("Bulk delete operation failed!"))