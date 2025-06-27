from rest_framework import serializers

from .models import Option, Question, Quiz


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="questions_per_attempt")

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "cover_image", "question_count"]


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "content"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "content", "options"]
