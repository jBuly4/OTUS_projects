from django.urls import path
from . import views

app_name = 'hasker_app'

urlpatterns = [
    path('', views.questions_list, name='questions_list'),
    path('<int:id>/', views.question_detail, name='question_detail'),
]
