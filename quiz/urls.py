from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
from .views import QuizViewSet, QuestionViewSet, ResultViewSet


router = SimpleRouter()
router.register("quizzes", QuizViewSet, basename="quiz")

questions_router = NestedSimpleRouter(router, "quizzes", lookup="quiz")
questions_router.register("questions", QuestionViewSet, basename="question")

results_router = NestedSimpleRouter(router, "quizzes", lookup="quiz")
results_router.register("results", ResultViewSet, basename="result")

urlpatterns = router.urls
urlpatterns += questions_router.urls
urlpatterns += results_router.urls
