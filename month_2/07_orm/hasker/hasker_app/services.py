"""This module provides functionality for database queries to avoid that logic inside views."""
from typing import Tuple

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
