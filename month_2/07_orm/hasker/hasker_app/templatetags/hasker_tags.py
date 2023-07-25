from django import template

from ..models import PostQuestion
from ..services import get_most_rated

register = template.Library()


@register.inclusion_tag('hasker_app/question/most_rated_questions.html')
def show_most_rated_questions(count=20):
    """Register inclusion tag to render trending section."""
    most_rated = get_most_rated(PostQuestion)[:count]

    return {'trending': most_rated}


@register.filter(name='clear_search_tag')
def clear_search_tag(query):
    return query.replace('tag:', '', 1)
