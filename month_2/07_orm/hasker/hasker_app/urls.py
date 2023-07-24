from django.urls import path
from . import views

app_name = 'hasker_app'

urlpatterns = [
    path('', views.questions_list, name='questions_list'),
    path('tag/<str:tag_title>/', views.questions_list, name='questions_list_by_tag'),
    path(
            '<int:year>/<int:month>/<int:day>/<slug:question_slug>',
            views.question_detail, name='question_detail'
    ),
    path('question/add/', views.add_question, name='add_question'),
    path('<int:question_id>/answer/', views.add_answer, name='add_answer'),
]
