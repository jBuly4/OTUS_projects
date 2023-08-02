from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import ProfileEditForm, UserEditForm, UserRegistrationForm
from .models import Profile


@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(
            request,
            'account/profile.html',
            {
                'section': 'profile',
                'user_profile': user_profile,
            }
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


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                    user_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            messages.success(request, 'Register success! Your profile has been created!')
            return render(
                    request,
                    'account/register_done.html',
                    {'new_user': new_user}
            )
    else:
        messages.info(request, 'Fill up the form to register!')
        user_form = UserRegistrationForm()

    return render(
            request,
            'account/register.html',
            {'user_form': user_form}
    )


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
                instance=request.user.profile,
                data=request.POST,
                files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            messages.error(request, 'Error updating your profile!')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
            request,
            'account/edit.html',
            {
                'user_form': user_form,
                'profile_form': profile_form
            }
    )
