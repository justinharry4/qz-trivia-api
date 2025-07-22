import logging

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.exceptions import NotFound
from rest_framework import status

from .models import Question, Quiz, Option, Result, AnsweredQuestion
from .serializers import QuizSerializer, QuestionSerializer, CreateResultSerializer, ResultSerializer


logger = logging.getLogger(__name__)


class QuizViewSet(
    ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = QuizSerializer

    def get_queryset(self):
        queryset = Quiz.objects.all()
        limit = self.request.query_params.get('limit', None)

        if limit and limit.isdigit() and int(limit) > 0:
            return queryset[:int(limit)]

        return queryset

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        logger.info('Quiz list fetched')
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Quiz retrieved - Quiz ID: {self.kwargs['pk']}")

        return super().retrieve(request, *args, **kwargs)


class QuestionViewSet(ListModelMixin, GenericViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_pk'])

        return (
            Question.objects.prefetch_related(
                Prefetch("options", queryset=Option.objects.order_by("?"))
            )
            .filter(quiz_id=quiz.id)
            .order_by("?")
        )[: quiz.questions_per_attempt]

    def list(self, request, *args, **kwargs):
        logger.info(f"Question list fetched - Quiz ID: {self.kwargs['quiz_pk']}")
        return super().list(request, *args, **kwargs)


class ResultViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    def get_queryset(self):
        ordered_questions_prefetch = Prefetch(
            'answered_questions',
            queryset=AnsweredQuestion.objects.order_by('position_in_quiz')
        )
        all_options_prefetch = Prefetch(
            'answered_questions__question__options',
            queryset=Option.objects.order_by("?")
        )
        return (
            Result.objects
                .filter(quiz_id=self.kwargs['quiz_pk'])
                .select_related('quiz')
                .prefetch_related(
                    ordered_questions_prefetch,
                    'answered_questions__selected_option',
                    all_options_prefetch
                )
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateResultSerializer

        return ResultSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        quiz_id = self.kwargs['quiz_pk']

        if self.action == "create":
            try:
                quiz = Quiz.objects.get(pk=quiz_id)
            except Quiz.DoesNotExist:
                quiz = None

            context['quiz'] = quiz

        return context

    def perform_create(self, serializer):
        quiz = serializer.context['quiz']

        if not quiz:
            raise NotFound(
                detail=f"The specified quiz of id `{self.kwargs['quiz_pk']}` "
                        "does not exist"
            )

        return serializer.save()

    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)

        instance = self.perform_create(create_serializer)

        prefetched_instance = self.get_queryset().get(pk=instance.id)
        return_serializer = ResultSerializer(prefetched_instance)

        logger.info(
            f"Result created - Result ID: {instance.id} - "
            f"Quiz ID: {instance.quiz.id}"
        )
        
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        logger.warning(
            f"Result retrieved - Result ID: {self.kwargs['pk']} - "
            f"Quiz ID: {self.kwargs['quiz_pk']}"
        )

        return super().retrieve(request, *args, **kwargs)


