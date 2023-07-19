from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, get_object_or_404

from .models import PostAnswer, PostQuestion
from .services import get_all_published


def questions_list(request):
    question_list = get_all_published(PostQuestion)
    paginator = Paginator(question_list, 20)
    page_number = request.GET.get('page', 1)
    try:
        questions = paginator.page(page_number)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    return render(
            request,
            'hasker_app/question/list.html',
            {'questions': questions}
    )


def question_detail(request, year, month, day, question_slug):
    question = get_object_or_404(
            PostQuestion,
            status=PostQuestion.Status.PUBLISHED,
            slug=question_slug,
            publish__year=year,
            publish__month=month,
            publish__day=day,
    )

    return render(
            request,
            'hasker_app/question/detail.html',
            {'question': question}
    )

# TODO: add answers like comments on question detail.
# TODO: non-authenticated users can see all questions and answers
# TODO: only authenticated users can answer and rate questions with answers

