from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    cover_image = models.ImageField(upload_to="quiz/images/", null=True)

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return f"Quiz(id={self.id}, title={self.title})"


class Question(models.Model):
    content = models.TextField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)


class Option(models.Model):
    content = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    duration = models.DurationField()


class AnsweredQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="answered_questions",
    )
