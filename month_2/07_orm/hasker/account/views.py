from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render
from django.urls import reverse_lazy


@login_required
def profile(request):
    return render(
            request,
            'account/profile.html',
            {'section': 'profile'}
    )


@login_required
def questions_of_user(request):
    return render(
            request,
            'hasker_app/question/user_questions_list.html',
            {'section': 'my_questions'}

    )

@login_required
def ask_questions(request):
    return render(
            request,
            'hasker_app/question/add_question.html.html',
            {'section': 'ask_question'}

    )


# to solve problem with: django.urls.exceptions.NoReverseMatch: Reverse for 'password_change_done' not found.
# 'password_change_done' is not a valid view function or pattern name.
# the problem is that I added namespace, solution is to override all future ClassViews wich use success_urls
class PassChange(PasswordChangeView):
    success_url = reverse_lazy('account:password_change_done')


class PassResetView(PasswordResetView):
    success_url = reverse_lazy('account:password_reset_done')


class PassResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('account:password_reset_complete')
