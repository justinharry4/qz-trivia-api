from django.db import transaction

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

class SimpleQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "content"]



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
    question = SimpleQuestionSerializer()
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
        correct_option = obj.question.options.all()[0]
        serializer = OptionSerializer(correct_option)
        return serializer.data


class ResultSerializer(serializers.ModelSerializer):
    quiz = SimpleQuizSerializer()
    answered_questions = AnsweredQuestionSerializer(many=True)
    percentage_score = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ["id", "quiz", "answered_questions", "percentage_score"]

    def get_percentage_score(self, obj):
        queryset = obj.answered_questions.all()
        serializer = AnsweredQuestionSerializer(queryset, many=True)
        answered_questions = serializer.data

        total_question_count = len(answered_questions)
        correct_question_count = 0

        for aq in answered_questions:
            selected_option = aq.get('selected_option', None) 
            if selected_option and aq['correct_option']['id'] == selected_option['id']:
                correct_question_count += 1

        return round((correct_question_count / total_question_count) * 100)

