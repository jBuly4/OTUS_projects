from django.urls import path
from . import views

app_name = 'hasker_app'

urlpatterns = [
    path('', views.questions_list, name='questions_list'),
    path(
            '<int:year>/<int:month>/<int:day>/<slug:question_slug>',
            views.question_detail, name='question_detail'
    ),
]
