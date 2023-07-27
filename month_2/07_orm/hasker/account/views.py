from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render

from .forms import LoginForm


def user_login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            clean_data = login_form.cleaned_data
            user = authenticate(
                    request,
                    username=clean_data['username'],
                    password=clean_data['password'],
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully!')
                else:
                    return HttpResponse('Disabled account!')
            else:
                return HttpResponse('Invalid login!')
    else:
        login_form = LoginForm()
    return render(
            request,
            'account/login.html',
            {'login_form': login_form}
    )


