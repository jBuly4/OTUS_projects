"""This module provides functionality for database queries to avoid that logic inside views."""
from typing import List

# import django.forms
# from django import forms
from django.db import models
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Tag


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


def _search(cls: models.Model, input_query: str, tag_search: bool = False) -> models.QuerySet:
    """
    Search in questions with user query.
    :param cls: model object
    :param input_query: string to be searched
    :return: results in queryset
    """
    if tag_search:
        question_list = get_questions_published(cls)
        tag_input = input_query.split(':')[1].strip()
        try:
            tag = get_object_or_404(Tag, title=tag_input)
            results = question_list.filter(tags__in=[tag])
        except Http404:
            results = cls.objects.none()

    else:
        search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
        search_query = SearchQuery(input_query)
        results = cls.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.3).order_by('-rank')

    return results.order_by('-rating', '-publish')
