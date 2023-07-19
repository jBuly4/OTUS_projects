from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .managers import PublishedManager


class PostQuestion(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField()
    publish = models.DateField(default=timezone.now())
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    status = models.CharField(
            max_length=2,
            choices=Status.choices,
            default=Status.DRAFT
    )
    author = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='post_question'
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def get_absolute_url(self):
        return reverse(
                'hasker_app:question_detail',
                args=[
                    self.publish.year,
                    self.publish.month,
                    self.publish.day,
                    self.slug
                ]
        )

    def __str__(self):
        return self.title


class PostAnswer(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    question_post = models.ForeignKey(
            PostQuestion,
            on_delete=models.CASCADE,
            related_name='post_answer'
    )
    body = models.TextField()
    publish = models.DateField(default=timezone.now())
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    status = models.CharField(
            max_length=2,
            choices=Status.choices,
            default=Status.DRAFT
    )
    author = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='post_answer'
    )
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def get_question_title(self):
        return self.question_post.title

    def __str__(self):
        return f'answer for {self.get_question_title()}'
