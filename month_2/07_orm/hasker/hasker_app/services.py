"""This module provides functionality for database queries to avoid that logic inside views."""
from typing import Dict, List

# import django.forms
# from django import forms
from django.db import models
from django.contrib.auth.models import User
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


def check_user_likes(obj: models.QuerySet, user: User, like: bool = False) -> bool:
    """Check user liked or disliked question or answer."""
    if like:
        return obj.users_like.filter(id=user.id).exists()
    return obj.users_dislike.filter(id=user.id).exists()


def rate(cls: models.Model, obj_id: int, user: User, like: bool = False) -> Dict:
    """
    Get published question/answer by its id and rate it.
    :param cls: model object
    :param obj_id: id of object
    :param user: user object
    :param like: True for increase, False for decrease rating
    :return: status of operation
    """
    try:
        object_to_be_rated = cls.published.get(id=obj_id)
        already_liked = object_to_be_rated.users_like.filter(id=user.id).exists()
        already_disliked = object_to_be_rated.users_dislike.filter(id=user.id).exists()

        if like:
            if already_liked:
                return {'status': 'Already liked', 'error': True}

            if already_disliked:
                object_to_be_rated.users_dislike.remove(user)
            object_to_be_rated.users_like.add(user)
            object_to_be_rated.increase_rating()

        else:
            if already_disliked:
                return {'status': 'Already disliked', 'error': True}

            if already_liked:
                object_to_be_rated.users_like.remove(user)
            object_to_be_rated.users_dislike.add(user)
            object_to_be_rated.decrease_rating()

        object_to_be_rated.save()
        return {'status': 'ok', 'error': False}

    except cls.DoesNotExist:
        return {'status': 'DoesNotExist', 'error': True}


def check_question_author(question_model: models.Model, answer_id: str, user_id: int) -> bool | None:
    """Check if outer user is the author of question."""
    author_id = question_model.published.filter(post_answer__id=answer_id)[0].author.id

    return author_id == user_id


def make_correct(cls: models.Model, obj_id: str, correct: bool = False) -> Dict:
    """
    Mark answer as correct by question author.
    :param cls: model object
    :param obj_id: id of object
    :param correct: status for answer
    :return: status of operation
    """
    status = {}
    try:
        answer = cls.published.get(id=obj_id)
        if correct:
            try:
                current_correct_answer = cls.published.get(question_post=answer.question_post, answer_is_correct=True)
                if current_correct_answer.id != answer.id:
                    current_correct_answer.answer_is_correct = False
                    current_correct_answer.save()
                    status['old_id'] = current_correct_answer.id
            except cls.DoesNotExist:
                pass
        answer.answer_is_correct = correct
        answer.save()
        status.update({'status': 'ok', 'error': False})
        return status

    except cls.DoesNotExist:
        return {'status': 'DoesNotExist', 'error': True}


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
        ).filter(rank__gte=0.1).order_by('-rank')

    return results.order_by('-rating', '-publish')


def get_user_question(cls: models.Model, username: str) -> models.QuerySet:
    """
    Get all users' questions.
    :param cls: model object
    :param username: username
    :return: queryset with questions asked by user
    """
    try:
        user_id = get_object_or_404(User, username=username)
        user_questions = cls.published.filter(author=user_id)
    except Http404:
        user_questions = cls.objects.none()

    return user_questions


def get_user_id(username: str, cls: models.Model = User) -> int:
    """
    Get user id.
    :param cls: User model object
    :param username: username from request
    :return: id
    """
    try:
        user_id = get_object_or_404(cls, username=username)
    except Http404:
        user_id = None

    return user_id
