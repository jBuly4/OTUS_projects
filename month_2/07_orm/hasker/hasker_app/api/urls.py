from django.urls import path

from . import views

app_name = 'hasker_app'

urlpatterns = [
    path('questions/', views.QuestionListView.as_view(), name='api_questions_list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='api_question_detail'),
    path('questions/<int:question_post>/answers/', views.AnswerView.as_view(), name='api_question_answers'),
    path('tags/', views.TagListView.as_view(), name='api_tags_list'),
    path('tags/<int:tag>/questions/', views.TagSortedQuestionsView.as_view(), name='api_sorted_by_tag'),
    path('accounts/profile/<int:user>/', views.ProfileView.as_view(), name='api_profile'),
    path('trendings/', views.TrendingView.as_view(), name='api_trendings'),
]