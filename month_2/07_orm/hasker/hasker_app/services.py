"""This module provides functionality for database queries to avoid that logic inside views."""
from django.db import models


def get_all_published(cls: models.Model):
    """
    Get all published objects from db for model.
    :param cls: model object
    :return: queryset
    """
    items = cls.published.all()
    return items
