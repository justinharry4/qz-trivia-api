from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
from .views import QuizViewSet, QuestionViewSet


router = SimpleRouter()
router.register("quizzes", QuizViewSet)

questions_router = NestedSimpleRouter(router, "quizzes", lookup="quiz")
questions_router.register("questions", QuestionViewSet, basename="question")

urlpatterns = router.urls
urlpatterns += questions_router.urls
