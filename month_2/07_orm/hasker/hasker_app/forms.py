from django import forms

from .models import PostAnswer, PostQuestion


class QuestionForm(forms.ModelForm):
    class Meta:
        model = PostQuestion
        fields = ['title', 'body', 'author', 'status']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = PostAnswer
        fields = ['body', 'author', 'status']