import logging

from django.core.management import BaseCommand
from django.db import transaction

from ...models import Quiz, Question, Option
from ...services.opentdb_client import OpenTDBClient, APIClientError


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialise database with public quiz data"

    def add_arguments(self, parser):
        parser.add_argument(
            "max_questions",
            help="Maximum number of questions fetched per category",
            type=int,
            default=50,
            nargs="?",
        )

    def handle(self, *args, **options):
        logger.info("Database seeding operation started")
        self.stdout.write("Seeding database...")

        self.quiz_counter = 0
        self.question_counter = 0
        self.option_counter = 0

        try:
            api_client = OpenTDBClient()
            categories = api_client.get_categories()
            api_client.set_token()
        except APIClientError:
            logger.error("Request to OpenTDB failed", exc_info=True)
            self.stdout.write(self.style.ERROR("Database seeding operation failed."))

            return

        logger.info(f"Total categories count: {len(categories)}")
        self.stdout.write(
            f"Quiz data for {len(categories)} quiz "
            "categories to be written to the database"
        )

        max_questions = options["max_questions"]

        for category in categories:
            available_questions = category["questions_count"]
            amount = (
                available_questions
                if max_questions > available_questions
                else max_questions
            )

            try:
                api_questions = api_client.get_questions_for_category(
                    category_id=category["id"], amount=amount
                )
            except APIClientError:
                logger.error("Request to OpenTDB failed", exc_info=True)
                continue

            try:
                with transaction.atomic():
                    quiz = Quiz.objects.create(title=category["name"])
                    self.quiz_counter += 1

                    options_map = self.create_questions(quiz, api_questions)
                    questions = Question.objects.filter(quiz_id=quiz.id)
                    self.create_options(questions, options_map)

                    logger.info(f"Quiz creation successful - Quiz ID: {quiz.id}")
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"`{category['name']}` quiz data written to db successfully!"
                        )
                    )
            except Exception:
                logger.error(
                    f"Quiz creation failed - {category['name']}", exc_info=True
                )
                self.stdout.write(
                    self.style.ERROR(f"Quiz creation failed - {category['name']}")
                )

        logger.info(
            f"Created quiz count: {self.quiz_counter}, "
            f"Created question count: {self.question_counter}, "
            f"Created option count: {self.option_counter}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{self.quiz_counter} quiz(zes), {self.question_counter} "
                f"questions(s), and {self.option_counter} option(s) have "
                "been added to the database"
            )
        )

    def calculate_question_tag(self, question):
        return question.content[:25] + question.content[-25:]

    def create_questions(self, quiz, api_questions):
        questions, options_map = [], {}

        for api_question in api_questions:
            question = Question(content=api_question["question"], quiz=quiz)
            questions.append(question)

            api_options = [api_question["correct_answer"]]
            api_options.extend(api_question["incorrect_answers"])

            tag = self.calculate_question_tag(question)
            options_map[tag] = api_options

        created_questions = Question.objects.bulk_create(questions)
        self.question_counter += len(created_questions)

        return options_map

    def create_options(self, questions, options_map):
        all_options = []

        for question in questions:
            tag = self.calculate_question_tag(question)
            api_options = options_map.pop(tag, None)

            if api_options:
                for idx, option_text in enumerate(api_options):
                    all_options.append(
                        Option(
                            content=option_text,
                            is_correct=(idx == 0),
                            question=question,
                        )
                    )

        created_options = Option.objects.bulk_create(all_options)
        self.option_counter += len(created_options)
