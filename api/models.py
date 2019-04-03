from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
from rest_framework.reverse import reverse

# Create your models here.

class Author(models.Model):
    author_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    url=models.URLField(blank=True)
    firstName=models.CharField(max_length=30,blank=True,null=True)
    lastName=models.CharField(max_length=30,blank=True)
    userName=models.CharField(max_length=30,blank=True)
    password=models.CharField(max_length=30,blank=True)
    hostName=models.URLField(blank=True)
    owner=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    githubUrl=models.URLField(blank=True)

    def __str__(self):
        return self.userName
    @classmethod
    def get_url(self,obj):
        return str(getattr(obj,'hostName'))+"/api/authors/"+str(getattr(obj,'author_id'))

class FriendRequest(models.Model):
    from_author= models.ForeignKey(Author,on_delete=models.CASCADE, related_name="friend_request_sent",null=True)
    to_author=models.ForeignKey(Author,on_delete=models.CASCADE, related_name="friend_request_recieved",null=True)
    created=models.DateTimeField(blank=True, null=True)
    accepted=models.BooleanField(default=False)
    regected=models.BooleanField(default=False)

    def __str__(self):
        return "You recieved a friend request from %s to %s"%(self.from_author, self.to_author)

class Friends(models.Model):
    author1=models.ForeignKey(Author,on_delete=models.CASCADE,related_name='friend1',null=True,blank=True)
    author1_url=models.URLField(null=True,blank=True)
    author2_url=models.URLField(null=True,blank=True)
    author2=models.ForeignKey(Author,on_delete=models.CASCADE,related_name='friend2',null=True,blank=True)
    date=models.DateTimeField(blank=True, null=True)

class Following(models.Model):
    follower = models.ForeignKey(Author,on_delete=models.CASCADE, related_name="follower",null=True)
    following = models.ForeignKey(Author,on_delete=models.CASCADE, related_name="following",null=True)
    created=models.DateTimeField(blank=True, null=True)

class Post(models.Model):
    PERMISSION_OPTIONS = (
        ("M", "me"),
        ("L", "permitted authors"),
        ("F", "my friends"),
        ("FF", "friends of friends"),
        ("FH", "friends on my host"),
        ("P", "public")
    )
    contentTypeChoice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base64'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    postid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.URLField(null=True, blank=True)
    origin = models.URLField(null=True, blank=True)
    contentType = models.CharField(max_length=32, choices=contentTypeChoice)
    publicationDate=models.DateTimeField()
    content=models.TextField()
    title=models.CharField(max_length=50)
    permission = models.CharField(max_length=2, choices=PERMISSION_OPTIONS, default='P')
    unlisted=models.BooleanField(default=False)
    author= models.ForeignKey(Author,related_name="auth",on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.title

class Categories(models.Model):
    post=models.ForeignKey(Post,related_name="post_categories",on_delete=models.CASCADE,null=True)
    category=models.CharField(max_length=50)


class VisibleToPost(models.Model):
    post=models.ForeignKey(Post,related_name="visible_post",on_delete=models.CASCADE,null=True)
    author=models.ForeignKey(Author,on_delete=models.CASCADE,null=True, blank=True)
    author_url=models.URLField(null=True)


class Comment(models.Model):
    contentTypeChoice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
    )
    comment=models.TextField()
    contentType = models.CharField(max_length=32, choices=contentTypeChoice,default='text/plain' )
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author=models.ForeignKey(Author, on_delete=models.CASCADE,null=True)
    postid=models.ForeignKey(Post,related_name="post_comment",on_delete=models.CASCADE,null=True)
    published=models.DateTimeField()

    def __str__(self):
        return self.comment

class Image(models.Model):

    post_id = models.ForeignKey(Post,related_name="post_image", on_delete=models.CASCADE,null=True)
    img = models.TextField()

class Node(models.Model):
    
    node_url=models.URLField()
    username=models.CharField(max_length=32, blank=True)
    password=models.CharField(max_length=32, blank=True)
    sharePosts=models.BooleanField()
    shareImages=models.BooleanField()


