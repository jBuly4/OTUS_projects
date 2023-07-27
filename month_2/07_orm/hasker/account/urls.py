from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # path('login/', views.user_login, name='user_login'),

    # urls for auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # urls for password change
    path('password-change/', views.PassChange.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    #urls for password reset
    path('password-reset/', views.PassResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>', views.PassResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # url for profile
    path('', views.profile, name='profile'),
]
