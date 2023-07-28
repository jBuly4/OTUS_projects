from django import forms

from .models import PostAnswer, PostQuestion


class QuestionForm(forms.ModelForm):

    tags = forms.CharField(
            max_length=250,
            help_text="Add tags in comma separated line. You can add only 3 tags!"
    )

    class Meta:
        model = PostQuestion
        fields = ['title', 'body', 'tags', 'status']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = PostAnswer
        fields = ['body', 'status']


class SearchForm(forms.Form):
    query = forms.CharField()
