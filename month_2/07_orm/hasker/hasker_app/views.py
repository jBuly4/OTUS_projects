from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404

from .forms import AnswerForm, QuestionForm, SearchForm
from .models import PostAnswer, PostQuestion, Tag
from .services import get_questions_published, get_similar_published_questions, increase_views, _search, \
    get_user_question, get_user_id


def questions_list(request, tag_title=None):
    question_list = get_questions_published(PostQuestion)

    tag = None
    if tag_title:
        tag = get_object_or_404(Tag, title=tag_title)
        question_list = question_list.filter(tags__in=[tag])

    question_list = question_list.annotate(answer_count=Count('post_answer'))
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
            {
                'questions': questions,
                'tag': tag,
            }
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
    increase_views(
            PostQuestion,
            question_id=question.id
    )
    question.refresh_from_db()

    answers = question.post_answer.filter(status=PostAnswer.Status.PUBLISHED)
    answer_form = AnswerForm()

    # similar questions
    question_tags_ids = question.tags.values_list('id', flat=True)
    similar_questions = get_similar_published_questions(
            PostQuestion,
            question_tags_ids,
            question.id
    )

    return render(
            request,
            'hasker_app/question/detail.html',
            {
                'question': question,
                'answers': answers,
                'answer_form': answer_form,
                'similar_questions': similar_questions,
            }
    )


def add_question(request):
    question = None
    user_id = get_user_id(request.user.username)

    if not request.user.is_authenticated and not user_id:
        return render(
                request,
                'registration/login.html',
        )

    if request.POST:
        question_form = QuestionForm(data=request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            tags_input = question_form.cleaned_data['tags']
            tags = [tag.rstrip() for tag in tags_input.split(',') if tag != '']

            if len(tags) > 3:
                question_form.add_error('tags', 'You can add up to 3 tags only!')
                return render(
                        request,
                        'hasker_app/question/add_question.html',
                        {'question_form': question_form}
                )

            question.generate_slug()
            question.author = user_id
            question.save()
            for tag in tags:
                tag_to_add, existed = Tag.objects.get_or_create(title=tag)
                question.tags.add(tag_to_add)
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
                'tags': answer,
                'answer_form': answer_form,
            }
    )


def tags_list(request):
    tags_lst = Tag.objects.all()

    paginator = Paginator(tags_lst, 10)
    page_number = request.GET.get('page', 1)
    try:
        tags = paginator.page(page_number)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)

    return render(
            request,
            'hasker_app/tags/list.html',
            {'tags': tags}
    )


def question_search(request):
    search_form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            if "tag:" in query:
                results = _search(PostQuestion, query, True)
            else:
                results = _search(PostQuestion, query)

    paginator = Paginator(results, 20)
    page_number = request.GET.get('page', 1)
    try:
        res = paginator.page(page_number)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)

    return render(
            request,
            'hasker_app/question/search.html',
            {
                'search_form': search_form,
                'query': query,
                'results': res
            }
    )


def user_questions(request):
    questions = get_user_question(PostQuestion, request.user.username)
    questions = questions.annotate(answer_count=Count('post_answer'))

    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page', 1)
    try:
        res = paginator.page(page_number)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)


    return render(
            request,
            'hasker_app/question/user_questions_list.html',
            {
                'user_questions': res,
            }
    )


# TODO: non-authenticated users can see all questions and answers
# TODO: only authenticated users can tags and rate questions with answers

