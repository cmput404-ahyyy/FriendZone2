from django.test import TestCase
from django.utils import timezone
from .models import Author, FriendRequest, Friends,Post,Comment, Following
from django.test import Client
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
import json
import uuid
from .views import unfriend, get_friends
""""""
from api.models import Author, FriendRequest, Friends,Post,Comment
from api.serializers import AuthorSerializer, FriendRequestSerializer, FriendsSerializer,PostSerializer,CommentSerializer, FollowingSerializer
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.utils.timezone import get_current_timezone, make_aware
from django.core import serializers
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
import sys
import unittest
from django.utils import timezone
import pytz
""""""

from .views import enroll_following, make_them_friends, unfollow, friend_request_to_remote, send_friend_request

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

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

class GetAllAuthorListViewTest(TestCase):
    def test_get_authors(self):

        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        credentials = body.get('token')
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + credentials
        response = self.client.post('api:authors_list')
        print(00000000, response.content, 11111111)
        self.assertEqual(response.status_code, 404)

class SignupViewTest(TestCase):
    def test_signup(self):
        # response = self.client.login(username="admin", password="admin")
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        self.assertEqual(response.status_code, 200)

class LoginViewTest(TestCase):
    def setUp(self):
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_login_inactive_user(self):
        # login
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:login'), data=data, format='json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 400, str(body))

    def test_login_logout_active_user(self):
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        # activate user
        user = User.objects.get(username='u3')
        user.is_active = True
        user.save()

        # login
        response = self.client.post(reverse('api:login'), data=data, format='json')
        self.assertEqual(response.status_code, 200)

        #logout
        body = response.content.decode('utf-8')
        body = json.loads(body)
        credentials = body.get('token')
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + credentials
        response = self.client.post(reverse('api:knox_logout'), data=data, format='json')
        self.assertEqual(response.status_code, 204, str(body))

class PostViewTests(TestCase):
    def setUp(self):
        # register
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        self.assertEqual(response.status_code, 200)  

        # activate user
        user = User.objects.get(username='u3')
        user.is_active = True
        user.save()

        # login
        response = self.client.post(reverse('api:login'), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.credentials = body.get('token')
        # print("line 121: ", str(body))

    def test_make_post(self):

        # make a post 
        data = {
            "permission": 'M',
            "content": 'post_content',
            "title": 'today_title',
            "images":[],
            "contentType": 'text/plain'
        }
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.post(reverse('api:auth_posts'), data=data, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))

    def test_get_public_posts(self):

        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.get(reverse('api:posts'), format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))

class ExistingPostViewTests(TestCase):
    def setUp(self):
        # register
        data = {'username': 'u3','password': 'u3', 'email':'a@b.ca'}
        response = self.client.post(reverse('api:signup'), data=data, format='json')
        self.assertEqual(response.status_code, 200)  

        # activate user
        user = User.objects.get(username='u3')
        user.is_active = True
        user.save()

        # login
        response = self.client.post(reverse('api:login'), data=data, format='json')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.credentials = body.get('token')
        
        # make a post
        data = {
            "permission": 'P',
            "content": 'post_content',
            "title": 'today_title',
            "images":[],
            "contentType": 'text/plain',

        }
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.post(reverse('api:auth_posts'), data=data, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))

        # get a post form public posts
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.get(reverse('api:posts'), format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        self.postid = body['posts'][0]['postid']

    def test_edit_delete_my_posts(self):
        # get profile to get current author id
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.get(reverse('api:author'), format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        author_id = body['author_id']

        #get my posts
        data = {"author_id": author_id}
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.post(reverse('api:get_authors_posts'), data=data, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        self.assertEqual(len(body), 1, 'check returned number of posts')
        post = body[0]
        postid = body[0]['postid']

        #edit my post
        post['content'] = 'new content'
        post['origin'] = 'https://test.com'
        post['author']['firstName'] = 'first name'
        post['author']['lastName'] = 'last name'
        post['author']['githubUrl'] = 'https://test.com'
        response = self.client.put(reverse('api:post_info', args = [postid]), data=post, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        self.assertEqual(body['success'], True, 'not successful')

        # check if it's updated
        data = {"author_id": author_id}
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.post(reverse('api:get_authors_posts'), data=data, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        self.assertEqual(body[0]['content'], 'new content', 'content is not updated')
        
        #delete my posts
        response = self.client.delete(reverse('api:post_info', args = [postid]), data=post, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        self.assertEqual(body['success'], True, 'not successful')

        #check if actually deleted
        data = {"author_id": author_id}
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.post(reverse('api:get_authors_posts'), data=data, format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        self.assertEqual(len(body), 0, 'check returned number of posts')

    def test_get_specific_posts(self):

        # get post using id
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.get(reverse('api:post_info', args=[self.postid]), format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))

    def test_post_and_get_comment(self):
        data = {
            "comment": "this is comment",
            "contentType": "text/plain",
            "authorid": "this is author id",
            "postid": self.postid,
        }
        # post comment
        # self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        # response = self.client.post(reverse('api:post_comments', args=[self.postid]), data=data, format='json', content_type='application/json')
        # body = response.content.decode('utf-8')
        # body = json.loads(body)
        # self.assertEqual(response.status_code, 201, str(body))
        # self.assertEqual(body['success'], True, str(body))

        #get comment
        self.client.defaults['HTTP_AUTHORIZATION'] = 'token ' + self.credentials
        response = self.client.get(reverse('api:post_comments', args=[self.postid]), format='json', content_type='application/json')
        body = response.content.decode('utf-8')
        body = json.loads(body)
        self.assertEqual(response.status_code, 200, str(body))
        # self.assertEqual(body['count'], 1, str(body))

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

    def test_send_request(self):
        # view = send_friend_request()
        request = self.factory.post(reverse('api:send_friend_request'), data=self.init_request, format='json')
        response = send_friend_request(request)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        # self.


class FriendRequestViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # for i in range(5,7):
        self.uuid1 = "06335e84-2872-4914-8c5d-3ed07d2a2f16"
        self.uuid2 = "06335e84-2872-4914-8c5d-3ed07d2a2f17"
        self.uuid3 = "06335e84-2872-4914-8c5d-3ed07d2a2f18"
        Author.objects.create(pk=uuid.UUID(self.uuid1), username='ftest1', password='test1111')
        Author.objects.create(pk=uuid.UUID(self.uuid2), username='ftest2', password='test1111')
        Author.objects.create(pk=uuid.UUID(self.uuid3), username='ftest2', password='test1111')
        self.init_request = {
            'from_author': uuid.UUID(self.uuid1),
            'to_author': uuid.UUID(self.uuid2)
        }
        self.reverse_request = {
            'from_author': uuid.UUID(self.uuid1),
            'to_author': uuid.UUID(self.uuid2)
        }
        self.init_request_2 = {
            'from_author': uuid.UUID(self.uuid1),
            'to_author': uuid.UUID(self.uuid3)
        }
        self.reverse_request_2 = {
            'from_author': uuid.UUID(self.uuid3),
            'to_author': uuid.UUID(self.uuid1)
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

    def test_get_friends_global(self):
        request = self.factory.post(reverse('api:send_friend_request'), data=self.init_request, format='json')
        response = send_friend_request(request)
        request = self.factory.post(reverse('api:send_friend_request'), data=self.reverse_request, format='json')
        response = send_friend_request(request)
        request = self.factory.post(reverse('api:send_friend_request'), data=self.init_request_2, format='json')
        response = send_friend_request(request)
        request = self.factory.post(reverse('api:send_friend_request'), data=self.reverse_request_2, format='json')
        response = send_friend_request(request)
        request = self.factory.get(reverse('api:get_global_friends', kwargs={'authorid': self.uuid1}), format='json')
        response = get_friends(request, self.uuid1)
        self.assertEqual(response.status_code,status.HTTP_200_OK)


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
