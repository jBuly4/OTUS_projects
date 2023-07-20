from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404

from .forms import QuestionForm, AnswerForm
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

    answers = question.post_answer.filter(status=PostAnswer.Status.PUBLISHED)
    # question_form = QuestionForm()
    answer_form = AnswerForm()
    return render(
            request,
            'hasker_app/question/detail.html',
            {
                'question': question,
                'answers': answers,
                # 'question_form': question_form,
                'answer_form': answer_form,
            }
    )


def add_question(request):
    question = None

    if request.POST:
        question_form = QuestionForm(data=request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.generate_slug()
            question.save()
    else:
        question_form = QuestionForm()

    return render(
            request,
            'hasker_app/question/add_question.html',
            {
                'question': question,
                'question_form': question_form,
            }
    )


@require_POST
def add_answer(request, question_id):
    answer = None
    question = get_object_or_404(
            PostQuestion,
            id=question_id,
            status=PostQuestion.Status.PUBLISHED,
    )

    answer_form = AnswerForm(data=request.POST)
    if answer_form.is_valid():
        answer = answer_form.save(commit=False)
        answer.question_post = question
        answer.save()

    return render(
            request,
            'hasker_app/question/add_answer.html',
            {
                'question': question,
                'answer': answer,
                'answer_form': answer_form,
            }
    )

# TODO: add answers like comments on question detail.
# TODO: non-authenticated users can see all questions and answers
# TODO: only authenticated users can answer and rate questions with answers

