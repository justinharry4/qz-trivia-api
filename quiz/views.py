from django.db.models import Prefetch

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, AllowAny

from .models import Question, Quiz, Option
from .serializers import QuizSerializer, QuestionSerializer


class QuizViewSet(
    ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return [AllowAny()]


class QuestionViewSet(ListModelMixin, GenericViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz = Quiz.objects.get(pk=self.kwargs['quiz_pk'])

        return (
            Question.objects.prefetch_related(
                Prefetch("options", queryset=Option.objects.order_by("?"))
            )
            .filter(quiz_id=quiz.id)
            .order_by("?")
        )[: quiz.questions_per_attempt]
