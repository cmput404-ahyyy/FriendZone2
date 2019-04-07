from django.test import TestCase
from django.utils import timezone
from .models import Author, FriendRequest, Friends,Post,Comment, Following
from django.test import Client
from django.urls import reverse
from django.db.models import Q
import json
import datetime
import base64
from django.contrib.auth.models import User
""""""
from api.models import Author, FriendRequest, Friends,Post,Comment
from api.serializers import AuthorSerializer, FriendRequestSerializer, FriendsSerializer,PostSerializer,CommentSerializer, FollowingSerializer
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.utils.timezone import get_current_timezone, make_aware
from django.core import serializers
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory
import sys
import unittest
from django.utils import timezone
import pytz
""""""
from .views import enroll_following, make_them_friends, unfollow, friend_request_to_remote, send_friend_request
from .views import unfriend
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
import uuid

# Create your tests here.
def create_author(f_name="A", l_name="B", u_name="101", pwd=101):
    return Author.objects.create(\
        firstName=f_name,\
        lastName=l_name,\
        userName=u_name,\
        password=pwd
    )

def create_friend_request(author_one, author_two):
    return FriendRequest.objects.create(\
        from_author=author_one,\
        to_author=author_two,\
        created=timezone.now()
    )

# class GetAllAuthorListViewTest(TestCase):
#     def test_get_authors(self):

#         data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
#         response = self.client.post(reverse('api:signup'), data=data, format='json')
#         body = response.content.decode('utf-8')
#         body = json.loads(body)
#         credentials = body.get('token')
#         self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + credentials
#         response = self.client.post('api:authors_list')
#         print(00000000, response.content, 11111111)
#         self.assertEqual(response.status_code, 404)

class SignupViewTest(TestCase):
    def test_signup(self):
        # response = self.client.login(username="admin", password="admin")
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        self.assertEqual(response.status_code, 200)

class LoginViewTest(TestCase):
    def test_login_inactive_user(self):
        # login first
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        credentials = body.get('token')
        data = {'username': 'u3','password': 'u3'}
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + credentials
        response = self.client.post(reverse('api:login'), data=data, format='json')
        # print(11111111111,response, 222222222222)
        self.assertEqual(response.status_code, 401)

    def test_login_active_user(self):

        # register
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')

        # activate user
        user = User.objects.get(username='u3')
        user.is_active = True
        user.save()

        # login
        response = self.client.post(reverse('api:login'), data=data, format='json')
        self.assertEqual(response.status_code, 200)

        # make a post
        body = response.content.decode('utf-8')
        body = json.loads(body)
        credentials = body.get('token')
        today_datetime = datetime.date.today()
        today_title = "test {:%b, %d %Y}".format(today_datetime)
        post_content = "This test post was created on {:%b, %d %Y}".format(today_datetime)

        data = {
            "permission": 'M',
            "content": post_content,
            "title": today_title,
            "images":[],
            "contentType": 'text/plain'
        }
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + credentials
        response2 = self.client.post(reverse('api:auth_posts'), data=data, format='json', content_type='application/json')
        body = response2.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response2.status_code, 200, str(body))

#    Traceback (most recent call last):
#   File "/Users/yonaelbekele/Documents/GitHub/FriendZone2/api/tests.py", line 123, in test_login_existing_author
#     self.assertEqual(response.status_code, 200)
# AssertionError: 400 != 200


    def test_login_existing_author(self):
        data = {'username': 'y','password': '1'}
        response = self.client.post(reverse('api-urls:login'), data=data, format='json')
        print('it worked')

        body = response.content.decode('utf-8')
        body = json.loads(body)

        print(response)
        print(body)
        self.assertEqual(response.status_code, 200)



class PostTestCase(TestCase):
    username = "u3"
    password = "u3"
    today_datetime = datetime.date.today()
    today_title = "test {:%b, %d %Y}".format(today_datetime)
    post_content = "This test post was created on {:%b, %d %Y}".format(today_datetime)


    def setup(self):
        self.user_1 = Author.objects.create_author(
            userName='y', firstName='yonael', lastName='bekele', password='1'
        )

    credentials = base64.b64encode(
            "{}:{}".format(username, password).encode()
        ).decode()

    client = Client(HTTP_AUTHORIZATION="Token {}".format(credentials))

    def test_make_a_post(self):
        Post.objects.create(author=self.user_1, title=today_title, content=post_content)
        response = client.get("/posts")
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        response = self.client.get(reverse('api:posts'))
        body = response.content.decode('utf-8')
        body = json.loads(body)
        print(body)
        #self.assertEqual(response.status_code, 200)



    # test get more than one post

    # test get one post


# class LoginRequestTests(TestCase):
#     def setUp(self):
#         self.client =
class FriendRequestViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # for i in range(5,7):
        self.uuid1 = "06335e84-2872-4914-8c5d-3ed07d2a2f16"
        self.uuid2 = "06335e84-2872-4914-8c5d-3ed07d2a2f17"
        Author.objects.create(pk=uuid.UUID(self.uuid1), username='ftest1', password='test1111')
        Author.objects.create(pk=uuid.UUID(self.uuid2), username='ftest2', password='test1111')
        self.init_request = {
            'from_author': uuid.UUID(self.uuid1),
            'to_author': uuid.UUID(self.uuid2)
        }
        self.reverse_request = {
            'from_author': uuid.UUID(self.uuid1),
            'to_author': uuid.UUID(self.uuid2)
        }


    def test_send_request(self):
        # view = send_friend_request()
        request = self.factory.post(reverse('api:send_friend_request'), data=self.init_request, format='json')
        response = send_friend_request(request)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        # self.

    def test_send_reverse_request(self):
        request = self.factory.post(reverse('api:send_friend_request'), data=self.init_request, format='json')
        response = send_friend_request(request)
        request = self.factory.post(reverse('api:send_friend_request'), data=self.reverse_request, format='json')
        response = send_friend_request(request)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertIsNotNone(Friends.objects.filter(Q(author1=uuid.UUID(self.uuid1) , author2=uuid.UUID(self.uuid2)) | Q(author1=uuid.UUID(self.uuid2) , author2=uuid.UUID(self.uuid1))))

    def test_unfollow(self):
        # unbefriend
        request = self.factory.post(reverse('api:unbefriend'), data=self.init_request, format='json')
        response = unfriend(request)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(0,len(Following.objects.filter(Q(follower=uuid.UUID(self.uuid1), following=uuid.UUID(self.uuid2)))))

class CheckFriendshipViewTests(TestCase):
    # def test_existing_friendship(self):
    #     response = self.client.get(reverse('api:author/<authorid>/friends/<authorid2>/', kwargs={}))
    pass
class FriendResultViewTests(TestCase):
    pass

class UnfriendViewTests(TestCase):
    pass

class RemoteServerTests(TestCase):
    def test_friend_request_to_remote(self):
        return
        print("TEST REMOTE")
        a1 = create_author(f_name="a1", l_name="a1", u_name="101", pwd=101)
        a1.save()
        a2 = create_author(f_name="a2", l_name="a2", u_name="102", pwd=101)
        a2.save()
        temp_dict = {"from_author":a1.author_id, "to_author":a2.author_id}
        # print(temp_dict)
        friend_request_to_remote(temp_dict)
        print("TEST REMOTE END")


#
# class UtilityTests(TestCase):
#     def test_getAuthor(self):
#         # Asserts Author is being created
#         try:
#             a1 = Author.objects.create(firstName='test_user', lastName='test_user_lastname', userName='test_userName', password='test')
#
#             self.assertTrue(Author.objects.get(firstName='test_user'))
#             self.assertTrue(Author.objects.get(userName='test_userName'))
#
#
#         except Exception as e:
#             print("Error!!!")
#
#     def test_createPost(self):
#         try:
#             a1 = Author.objects.create(firstName='test_user', lastName='test_user_lastname', userName='test_userName', password='test')
#             self.assertTrue(Author.objects.get(firstName='test_user'))
#             self.assertTrue(Author.objects.get(userName='test_userName'))
#
#         except Exception as e:
#             print("Error!!!")
#
#         p1 = Post.objects.create(publicationDate= timezone.now() ,content='this is a test', title='test', permission = "P", author = a1)
#
#         self.assertTrue(Post.objects.get(title='test'))
#
#     def test_make_them_friends(self):
#         a1 = create_author(f_name="a1", l_name="a1", u_name="101", pwd=101)
#         a1.save()
#         a2 = create_author(f_name="a2", l_name="a2", u_name="102", pwd=101)
#         a2.save()
#         fr = create_friend_request(a1, a2)
#         fr.save()
#         make_them_friends(a1, a2, fr)
#
#         try:
#             check_user = Author.objects.get(pk=a2.pk)
#             #print("Saved")
#         except Exception as e:
#             print("Error!!")
#
#         # no friend request
#         result0 = False
#         try:
#             result0 = FriendRequest.objects.get(pk=fr.pk)
#         except FriendRequest.DoesNotExist:
#             result0 = False
#         self.assertFalse(result0)
#         # have entry in friends
#         result = False
#         try:
#             result = Friends.objects.filter( Q(author1=a1, author2=a2) | Q(author2=a1, author1=a2)).exists()
#
#             self.assertTrue(result)
#             # print(111,Friends.objects.filter( Q(author1=a1), Q(author2=a2) | Q(author2=a1), Q(author1=a2)),222)
#         except Friends.DoesNotExist:
#             result = False
#         self.assertTrue(result)
#
#
#     def test_enroll_following(self):
#         a1 = create_author(f_name="a1", l_name="a1", u_name="101", pwd=101)
#         a1.save()
#         a2 = create_author(f_name="a2", l_name="a2", u_name="102", pwd=101)
#         a2.save()
#         temp_dict = {"requester_id" :a1 , "requestee_id":a2}
#         enroll_following(temp_dict)
#         try:
#             result = Following.objects.filter(follower=a1, following=a2)
#         except Friends.DoesNotExist:
#             result = False
#         self.assertTrue(result)
#
#     def test_unfollow(self):
#         a1 = create_author(f_name="a1", l_name="a1", u_name="101", pwd=101)
#         a1.save()
#         a2 = create_author(f_name="a2", l_name="a2", u_name="102", pwd=101)
#         a2.save()
#         temp_dict = {"requester_id" :a1 , "requestee_id":a2}
#         enroll_following(temp_dict)
#         temp_dict = {"follower" :a1 , "following":a2}
#         unfollow(temp_dict)
#         try:
#             result = Following.objects.filter(follower=a1, following=a2).exists()
#             #print(result)
#         except Friends.DoesNotExist:
#             result = True
#         self.assertFalse(result)
