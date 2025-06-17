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
    default_question_count = 15

    def get_queryset(self):
        return (
            Question.objects.prefetch_related(
                Prefetch("options", queryset=Option.objects.order_by("?"))
            )
            .filter(quiz_id=self.kwargs["quiz_pk"])
            .order_by("?")
        )[: self.default_question_count]
