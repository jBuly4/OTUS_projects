from django.shortcuts import render, get_object_or_404

from .models import PostAnswer, PostQuestion
from .services import get_all_published


def questions_list(request):
    questions = get_all_published(PostQuestion)

    return render(
            request,
            'hasker_app/question/list.html',
            {'questions': questions}
    )


def question_detail(request, id):
    question = get_object_or_404(
            PostQuestion,
            id=id,
            status=PostQuestion.Status.PUBLISHED
    )

