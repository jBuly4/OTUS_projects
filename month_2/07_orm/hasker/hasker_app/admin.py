from django.contrib import admin
from .models import PostAnswer, PostQuestion, Tag


@admin.register(PostQuestion)
class PostQuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']


@admin.register(PostAnswer)
class PostAnswerAdmin(admin.ModelAdmin):
    list_display = ['question_post', 'author', 'publish', 'status', 'rating']
    list_filter = ['status', 'created', 'publish', 'author', 'rating']
    search_fields = ['question_post', 'body']
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title']
    list_filter = ['title']
    search_fields = ['title']
    ordering = ['title']
