from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary_storage.storage import MediaCloudinaryStorage


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    cover_image = models.ImageField(upload_to="images/", null=True, storage=MediaCloudinaryStorage())
    questions_per_attempt = models.PositiveSmallIntegerField(
        default=15, validators=[MinValueValidator(1), MaxValueValidator(150)]
    )

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
    duration = models.DurationField(null=True)


class AnsweredQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, null=True, on_delete=models.CASCADE)
    position_in_quiz = models.PositiveSmallIntegerField()
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="answered_questions",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['result_id', 'position_in_quiz'],
                name="unique_position_in_quiz"
            )
        ]