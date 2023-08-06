import os

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from account.models import Profile
from hasker_app.api.serializers import AnswerSerializer, ProfileSerializer, QuestionSerializer, TagSerializer
from hasker_app.models import PostAnswer, PostQuestion, Tag
from hasker_app.services import get_questions_published
from dotenv import load_dotenv


load_dotenv()


class QuestionListView(generics.ListAPIView):
    queryset = PostQuestion.published.all()
    serializer_class = QuestionSerializer


class QuestionDetailView(generics.RetrieveAPIView):
    queryset = PostQuestion.published.all()
    serializer_class = QuestionSerializer


class AnswerView(generics.ListAPIView):
    serializer_class = AnswerSerializer
    lookup_field = 'question_post'

    def get_queryset(self):
        query = PostAnswer.published.filter(question_post=self.kwargs['question_post']). \
            order_by('-rating', 'publish')

        return query


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagSortedQuestionsView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        tag = get_object_or_404(Tag, id=self.kwargs['tag'])
        questions = get_questions_published(PostQuestion)
        question_filtered_by_tag = questions.filter(tags__in=[tag]).order_by('-rating', '-publish')

        return question_filtered_by_tag


class ProfileView(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    lookup_field = 'user'

    def get_queryset(self):
        return Profile.objects.all()


class TrendingView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    trending_num = int(os.getenv('TRENDS_NUM'))
    queryset = PostQuestion.published.order_by('-rating', '-publish')[:trending_num]
