"""This module provides functionality for database queries to avoid that logic inside views."""
from typing import List

from django import forms
from django.db import models


def get_questions_published(cls: models.Model) -> models.QuerySet:
    """
    Get all published objects from db for model.
    :param cls: model object
    :return: queryset
    """
    items = cls.published.all()
    return items


def get_similar_published_questions(cls: models.Model, tags_ids: List, question_id: int) -> models.QuerySet:
    """
    Get all similar published questions.
    :param cls: model object
    :param question_id: question to be exluded from db search
    :param tags_ids: list with tags ids
    :return: queryset - questions filtered by same amount of tags
    """
    similar_questions = cls.published.filter(tags__in=tags_ids).exclude(id=question_id)
    similar_questions = similar_questions.annotate(same_tags=models.Count('tags')) \
                                         .order_by('-same_tags', '-publish')[:3]

    return similar_questions


def get_most_rated(cls: models.Model) -> models.QuerySet:
    """
    Get most rated questions ordered by rating and by date.
    :param cls: model object
    :return: queryset - questions ordered by rating from newest to oldest
    """
    most_rated = cls.published.order_by('-rating', '-publish')

    return most_rated


def increase_views(cls: models.Model, question_id: int) -> None:
    """
    Increase safely views of question using models.F()
    :param cls: model object
    :param question_id: id of question
    """
    cls.published.filter(id=question_id).update(views=models.F('views') + 1)

