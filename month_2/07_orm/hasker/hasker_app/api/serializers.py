from django.contrib.auth.models import User
from rest_framework import serializers

from account.models import Profile
from hasker_app.models import PostAnswer, PostQuestion, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'photo']


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = PostQuestion
        fields = ['id', 'title', 'author', 'body', 'tags', 'status', 'rating']


class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    question_id = serializers.ReadOnlyField(source='question.id')

    class Meta:
        model = PostAnswer
        fields = ['id', 'question_id', 'author', 'body', 'status']

