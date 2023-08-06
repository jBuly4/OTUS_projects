from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from hasker_app.models import PostQuestion, PostAnswer, Tag
from account.models import Profile


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
