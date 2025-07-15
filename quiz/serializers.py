from django.db import transaction
from django.utils.functional import cached_property

from rest_framework import serializers

from .models import Option, Question, Quiz, Result, AnsweredQuestion


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="questions_per_attempt")

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "cover_image", "question_count"]


class SimpleQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id", "title"]


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "content"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "content", "options"]


class SimpleAnsweredQuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    question_number = serializers.IntegerField()


class CreateResultSerializer(serializers.Serializer):
    answered_questions = SimpleAnsweredQuestionSerializer(many=True)

    def validate_answered_questions(self, answered_questions):
        errors = {}
        question_ids, option_ids, question_numbers = [], [], []
        quiz = self.context['quiz']

        if len(answered_questions) == 0:
            raise serializers.ValidationError(
                "This field must be a list of one or more items"
            )

        for entry in answered_questions:
            question_ids.append(entry['question_id'])
            question_numbers.append(entry['question_number'])

            if entry['option_id'] != 0:
                option_ids.append(entry['option_id'])

        if Question.objects.filter(pk__in=question_ids).count() < len(question_ids):
            errors["question_id"] = "One or more invalid question ids were passed"
        elif quiz:
            all_question_ids = (
                Question.objects
                    .filter(quiz=quiz)
                    .values_list('id', flat=True)
            )

            if set(question_ids) - set(all_question_ids):
                errors["question_id"] = (
                    f"One or more invalid question ids for quiz of pk `{quiz.id}`"
                )

        if Option.objects.filter(pk__in=option_ids).count() < len(option_ids):
            errors["option_id"] = "One or more invalid option ids were passed"

        if len(question_numbers) != len(set(question_numbers)):
            errors["question_number"] = "Question numbers must be unique"

        if errors:
            raise serializers.ValidationError(errors)

        return answered_questions

    def create(self, validated_data):
        with transaction.atomic():
            result = Result.objects.create(quiz=self.context['quiz'])

            answered_questions = [
                AnsweredQuestion(
                    question_id=aq["question_id"],
                    selected_option_id=aq["option_id"] or None,
                    position_in_quiz=aq["question_number"],
                    result=result
                ) for aq in validated_data["answered_questions"]
            ]

            AnsweredQuestion.objects.bulk_create(answered_questions)

            return result


class AnsweredQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    selected_option = OptionSerializer()
    question_number = serializers.IntegerField(source="position_in_quiz")
    correct_option = serializers.SerializerMethodField()

    class Meta:
        model = AnsweredQuestion
        fields = [
            "id",
            "question",
            "selected_option",
            "correct_option",
            "question_number"
        ]

    def get_correct_option(self, obj):
        options = obj.question.options.all()
        correct_option = next((opt for opt in options if opt.is_correct))
        serializer = OptionSerializer(correct_option)
        return serializer.data


class ResultSerializer(serializers.ModelSerializer):
    quiz = SimpleQuizSerializer()
    answered_questions = AnsweredQuestionSerializer(many=True)
    total_answered = serializers.SerializerMethodField()
    total_correct = serializers.SerializerMethodField()
    percentage_score = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            "id",
            "quiz",
            "answered_questions",
            "total_answered",
            "total_correct",
            "percentage_score",
        ]

    @cached_property
    def _answered_questions(self):
        return self.instance.answered_questions.all()

    @cached_property
    def _total_correct(self):
        queryset = self._answered_questions
        serializer = AnsweredQuestionSerializer(queryset, many=True)
        total_correct = 0
        
        for aq in serializer.data:
            selected_option = aq.get('selected_option', None)
            if selected_option and aq['correct_option']['id'] == selected_option['id']:
                total_correct += 1

        return total_correct

    def get_total_answered(self, obj):
        return len(self._answered_questions)

    def get_total_correct(self, obj):
        return self._total_correct

    def get_percentage_score(self, obj):
        total_answered = len(self._answered_questions)
        total_correct = self._total_correct

        return (
            round((total_correct / total_answered) * 100, 1)
            if total_answered else 0
        )

