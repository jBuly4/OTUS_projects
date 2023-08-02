from django.urls import path
from . import views

app_name = 'hasker_app'

urlpatterns = [
    path('', views.questions_list, name='questions_list'),
    path('tag/', views.tags_list, name='tags_list'),
    path('tag/<str:tag_title>/', views.questions_list, name='questions_list_by_tag'),
    path(
            '<int:year>/<int:month>/<int:day>/<slug:question_slug>',
            views.question_detail, name='question_detail'
    ),
    path('questions/sort_by/<str:sort_by>/', views.questions_list, name='questions_list_sorted'),
    path('question/add/', views.add_question, name='add_question'),
    path('question/like/', views.make_like, name='question_like'),
    path('answer/like/', views.make_like, name='answer_like'),
    path('answer/correct/', views.make_like, name='make_correct'),
    path('question/my/', views.user_questions, name='user_questions'),
    path('<int:question_id>/add_answer/', views.add_answer, name='add_answer'),
    path('search/', views.question_search, name='question_search'),
]
