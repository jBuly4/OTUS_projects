import os

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from hasker_app.models import PostQuestion, PostAnswer, Tag
from account.models import Profile


# There are no models tests, because all their field and methods are tested in API and VIEWS


# API tests

class TestQuestionListView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_case_user', password='test_case_pass')
        self.question = PostQuestion.objects.create(
                title='Test question',
                body='Test content',
                author=self.user,
                status='PB',
        )
        self.tag = Tag.objects.create(title='tag1000')
        self.question.tags.add(self.tag)

    def tearDown(self):
        self.user.delete()
        self.question.delete()
        self.tag.delete()

    def test_question_list(self):
        url = reverse('api:api_questions_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Test question')
        self.assertEqual(response.data[0]['body'], 'Test content')
        self.assertEqual(response.data[0]['author'], self.user.username)
        self.assertEqual(response.data[0]['tags'][0]['title'], self.tag.title)
        self.assertEqual(response.data[0]['status'], 'PB')


class TestQuestionDetailView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_case_user', password='test_case_pass')
        self.question = PostQuestion.objects.create(
                title='Test question',
                body='Test content',
                author=self.user,
                status='PB',
        )
        self.tag = Tag.objects.create(title='tag1000')
        self.question.tags.add(self.tag)

    def tearDown(self):
        self.user.delete()
        self.question.delete()
        self.tag.delete()

    def test_question_detail(self):
        url = reverse('api:api_question_detail', kwargs={'pk': self.question.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test question')
        self.assertEqual(response.data['body'], 'Test content')
        self.assertEqual(response.data['author'], self.user.username)
        self.assertEqual(response.data['tags'][0]['title'], self.tag.title)
        self.assertEqual(response.data['status'], 'PB')


class TestAnswerView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_case_user', password='test_case_pass')
        self.question = PostQuestion.objects.create(title='Test question', body='Test content', author=self.user)
        self.answer1 = PostAnswer.objects.create(
                body='Test answer 1',
                question_post=self.question,
                author=self.user,
                status='PB',
        )
        self.answer2 = PostAnswer.objects.create(
                body='Test answer 2',
                question_post=self.question,
                author=self.user,
                status='PB'
        )

    def tearDown(self):
        self.user.delete()
        self.question.delete()
        self.answer1.delete()
        self.answer2.delete()

    def test_answers_list(self):
        url = reverse('api:api_question_answers', kwargs={'question_post': self.question.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['body'], 'Test answer 1')
        self.assertEqual(response.data[0]['author'], self.user.username)
        self.assertEqual(response.data[0]['status'], 'PB')
        self.assertEqual(response.data[1]['body'], 'Test answer 2')
        self.assertEqual(response.data[1]['author'], self.user.username)
        self.assertEqual(response.data[1]['status'], 'PB')  # DF will not be sent


class TestProfileView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_case_user', password='test_case_pass')
        self.profile = Profile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        # self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.profile.delete()
        self.token.delete()

    def test_profile_view(self):
        url = reverse('api:api_profile', kwargs={'user': self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], self.user.id)  # don't forget which field you serialize and how
        # to parse them
        self.assertEqual(response.data['user']['username'], self.user.username)


class TestTrendingView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_case_user', password='test_case_pass')
        self.question1 = PostQuestion.objects.create(
                title='Test question1',
                body='Test content1',
                author=self.user,
                rating=100,
                status='PB'
            )
        self.question2 = PostQuestion.objects.create(
                title='Test question2',
                body='Test content2',
                author=self.user,
                rating=0,
                status='PB'
        )

    def tearDown(self):
        self.user.delete()
        self.question1.delete()
        self.question2.delete()

    def test_trending_list(self):
        url = reverse('api:api_trendings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], self.question1.title)
        self.assertEqual(response.data[0]['rating'], self.question1.rating)
        self.assertEqual(response.data[1]['title'], self.question2.title)
        self.assertEqual(response.data[1]['rating'], self.question2.rating)
        self.question1.increase_rating()
        self.question1.save()
        self.question2.increase_rating()
        self.question2.save()
        response = self.client.get(url)
        self.assertEqual(response.data[0]['rating'], self.question1.rating)
        self.assertEqual(response.data[1]['rating'], self.question2.rating)


class TestTagListView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.tag1 = Tag.objects.create(title='tag1000')
        self.tag2 = Tag.objects.create(title='tag2000')

    def tearDown(self):
        self.tag1.delete()
        self.tag2.delete()

    def test_tag_list(self):
        url = reverse('api:api_tags_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1]['title'], 'tag1000')
        self.assertEqual(response.data[0]['title'], 'tag2000')


class TestTagSortedQuestionsView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='test_case_user', password='test_case_pass')
        self.user2 = User.objects.create_user(username='test_case_user2', password='test_case_pass2')
        self.tag1 = Tag.objects.create(title='tag1000')
        self.tag2 = Tag.objects.create(title='tag2000')
        self.tags = {1: self.tag1, 2: self.tag2}
        self.question1 = PostQuestion.objects.create(
                title='Test question1',
                body='Test content1',
                author=self.user1,
                status='PB'
        )
        self.question2 = PostQuestion.objects.create(
                title='Test question2',
                body='Test content2',
                author=self.user2,
                status='PB'
        )
        self.question1.tags.add(self.tag1)
        self.question2.tags.add(self.tag2)
        self.questions = {1: self.question1, 2: self.question2}

    def tearDown(self):
        self.tag1.delete()
        self.tag2.delete()
        self.user1.delete()
        self.user2.delete()
        self.question1.delete()
        self.question2.delete()
        del self.tags
        del self.questions

    def test_tag_list(self):
        for i in [1, 2]:
            url = reverse('api:api_sorted_by_tag', kwargs={'tag': i})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data[0]['title'], self.questions[i].title)
            self.assertEqual(response.data[0]['body'], self.questions[i].body)
            self.assertEqual(response.data[0]['author'], self.questions[i].author.username)
            self.assertEqual(response.data[0]['tags'][0]['title'], self.tags[i].title)


# VIEWS tests


class QuestionsListViewTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(title='tag1')
        self.tag2 = Tag.objects.create(title='tag2')
        self.user = User.objects.create_user(username='test_user', password='test_pass')

        self.questions = [
            PostQuestion.objects.create(
                    title='Question 1',
                    body='BodyQuestion 1',
                    author=self.user,
                    rating=3,
                    publish=timezone.now(),
                    status='PB'
            ),
            PostQuestion.objects.create(
                    title='Question 2',
                    body='BodyQuestion 2',
                    author=self.user,
                    rating=5,
                    publish=timezone.now() - timezone.timedelta(days=2),
                    status='PB'
            ),
            PostQuestion.objects.create(
                    title='Question 3',
                    body='BodyQuestion 3',
                    author=self.user,
                    rating=2,
                    publish=timezone.now() - timezone.timedelta(days=2),
                    status='PB'
            ),
            PostQuestion.objects.create(
                    title='Question 4',
                    body='BodyQuestion 4',
                    author=self.user,
                    rating=1,
                    publish=timezone.now() - timezone.timedelta(days=3),
                    status='PB'
            ),
        ]
        self.questions[0].tags.add(self.tag1)
        self.questions[1].tags.add(self.tag1)
        self.questions[2].tags.add(self.tag2)
        for q in self.questions:
            q.generate_slug()
            q.save()

    def tearDown(self) -> None:
        self.user.delete()
        for quest in self.questions:
            quest.delete()
        self.tag2.delete()
        self.tag1.delete()

    def test_questions_list(self):
        url = reverse('hasker_app:questions_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Question 1')
        self.assertContains(response, 'Question 2')
        self.assertContains(response, 'Question 3')
        self.assertContains(response, 'Question 4')

    def test_questions_list_sort_by_date(self):
        url = reverse('hasker_app:questions_list_sorted', kwargs={'sort_by': 'date'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='hasker_app/question/list.html')
        # later check order with beautiful soup

    def test_questions_list_sort_by_rating(self):
        url = reverse('hasker_app:questions_list_sorted', kwargs={'sort_by': 'rating'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='hasker_app/question/list.html')

    def test_questions_list_filter_by_tag(self):
        url = reverse('hasker_app:questions_list_by_tag', kwargs={'tag_title': 'tag1'})
        response = self.client.get(url)
        self.assertContains(response, 'Question 1')
        # self.assertNotContains(response, 'Question 3')  # but it is in trendings, TODO: add bs4 parsing for this cases
        self.assertTemplateUsed(response, template_name='hasker_app/question/list.html')


class AddQuestionTest(TestCase):

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.url = reverse('hasker_app:add_question')

    def tearDown(self) -> None:
        self.user.delete()
        self.client.logout()

    def test_add_question_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hasker_app/question/add_question.html')

    def test_add_question_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_add_question_with_tags(self):
        data = {
            'title': 'Test question',
            'body': 'Test body',
            'status': 'PB',
            'tags': 'tag1, tag2, tag3'
        }
        response = self.client.post(self.url, data=data)
        question = PostQuestion.published.get(title='Test question')
        self.assertEqual(question.title, 'Test question')
        self.assertEqual(question.body, 'Test body')
        self.assertEqual(question.author.username, self.username)

        question_tags = [tag.title for tag in question.tags.all()]
        self.assertEqual(question_tags, ['tag3', 'tag2', 'tag1'])  # tags are sorted from new to old

    def test_add_question_with_more_than_three_tags(self):
        data = {
            'title': 'Test question',
            'body': 'Test body',
            'status': 'PB',
            'tags': 'tag1, tag2, tag3, tag4'
        }
        response = self.client.post(self.url, data=data)
        self.assertFormError(response, 'question_form', 'tags', 'You can add up to 3 tags only!')


class AddAnswerTest(TestCase):

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.question = PostQuestion.objects.create(
                title='Test question',
                body='Test body',
                author=self.user,
                status=PostQuestion.Status.PUBLISHED,
        )
        self.question.generate_slug()
        self.question.save()
        self.url = reverse('hasker_app:add_answer', kwargs={'question_id': self.question.id})

    def tearDown(self) -> None:
        self.user.delete()
        self.question.delete()
        self.client.logout()

    def test_add_answer_to_question(self):
        data = {
            'body': 'Test answer',
            'status': 'PB'
        }
        response = self.client.post(self.url, data=data)
        answer = PostAnswer.published.get(question_post=self.question)
        self.assertEqual(answer.body, 'Test answer')
        self.assertEqual(answer.author, self.user)

    def test_add_answer_with_invalid_form(self):
        data = {
            'body': '',
        }
        response = self.client.post(self.url, data=data)
        self.assertFalse(response.context['answer_form'].is_valid())

    def test_add_answer_with_invalid_question(self):
        invalid_url = reverse('hasker_app:add_answer', kwargs={'question_id': 9999})
        response = self.client.post(invalid_url, data={'body': 'Test answer'})
        self.assertEqual(response.status_code, 404)
