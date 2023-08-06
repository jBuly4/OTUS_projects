from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .managers import PublishedManager


class Tag(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title


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
    rating = models.IntegerField(default=0)
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
    tags = models.ManyToManyField(
            Tag,
            related_name='question'
    )
    views = models.PositiveIntegerField(default=0)
    users_like = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='questions_liked',
            blank=True
    )
    users_dislike = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='questions_disliked',
            blank=True
    )

    objects = models.Manager()
    published = PublishedManager()
    # TODO: add rating field and ordering by it. Rating is a model.

    class Meta:
        ordering = ['-rating', '-publish']
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

    def generate_slug(self):
        self.slug = slugify(self.title)

    def increase_rating(self):
        self.rating += 1

    def decrease_rating(self):
        self.rating -= 1

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
    rating = models.IntegerField(default=0)
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
    users_like = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='answers_liked',
            blank=True
    )
    users_dislike = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='answers_disliked',
            blank=True
    )
    answer_is_correct = models.BooleanField(blank=True, default=False)
    objects = models.Manager()
    published = PublishedManager()

    # TODO: add rating field and ordering by it. Rating is a model.

    class Meta:
        ordering = ['-rating', '-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def get_question_title(self):
        return self.question_post.title

    def increase_rating(self):
        self.rating += 1

    def decrease_rating(self):
        self.rating -= 1

    def __str__(self):
        return f'Answer for {self.get_question_title()} by {self.author.username}'
