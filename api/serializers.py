from rest_framework import serializers
from .models import Author, FriendRequest, Friends,Post,Comment,VisibleToPost,Categories, Following,Image
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.contrib.auth.models import Permission
from rest_framework.relations import HyperlinkedIdentityField
from .pagination import CustomPagination,CommentPagination
 



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email','password')
        extra_kwargs={'password':{'write_only':True}}

    def create(self,validated_data):
        user=User.objects.create_user(validated_data['username'],validated_data['email'],validated_data['password'])
        author=Author.objects.create(userName=validated_data['username'], password=validated_data['password'],owner=user,hostName="https://project-cmput404.herokuapp.com")
        auth=Author.objects.filter(owner=user)
        url=auth[0].get_url(auth[0])
        auth.update(url=url)
        return user

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()

    def validate(self,data):
        user=authenticate(**data)
        print(user)
        if user and user.is_active:
            return user
        elif user and not user.is_active:
            raise serializers.ValidationError("Please Wait till we authorize you")
        else:
            raise serializers.ValidationError("Incorrect Crendentials")


class AuthorSerializer(serializers.ModelSerializer):
    firstName=serializers.CharField(required=False)
    lastName=serializers.CharField(required=False)
    userName=serializers.CharField(required=False)
    hostName=serializers.URLField(read_only=True)
    githubUrl=serializers.URLField(required=False)
    class Meta:
        model = Author
        fields=['url','author_id','firstName','lastName','userName','hostName','githubUrl']

    def update(self, instance, validated_data):
        instance.firstName = validated_data.get('firstName', instance.firstName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.userName = validated_data.get('userName', instance.userName)
        instance.githubUrl = validated_data.get('githubUrl', instance.githubUrl)
        instance.save()
        return instance


class FriendRequestSerializer(serializers.ModelSerializer):
    # pk = serializers.PrimaryKeyRelatedField(queryset=FriendRequest.objects.all())
    created = serializers.DateTimeField(default=timezone.now())
    accepted = serializers.BooleanField(default=False)
    regected = serializers.BooleanField(default=False)

    class Meta:
        model=FriendRequest
        fields=('pk','from_author',
        'to_author',
        'created','accepted',
        'regected')

    def create(self, validated_data):
        new_instance = FriendRequest.objects.create(\
            from_author=validated_data.get('from_author'),\
            to_author=validated_data.get('to_author'),\
            created=timezone.now(),\
            accepted=False,\
            regected=False
        )

        new_instance.save()

        return new_instance

    def update(self, instance, validated_data):
        instance.accepted = validated_data.get("accepted")
        instance.regected = validated_data.get("regected")
        instance.save()
        return instance


class FriendsSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(default=datetime.now())
    author1=AuthorSerializer(required=False)
    author2=AuthorSerializer(required=False)
    class Meta:
        model=Friends
        fields=('pk','author1',
        'author2',
        'date')
    def create(self, validated_data):
        # print(111, validated_data, 222)
        new_instance = Friends.objects.create(\
            author1=validated_data.get('to_author'),\
            author2=validated_data.get('from_author'),\
            date=timezone.now()
        )

        new_instance.save()

        return new_instance

class VisibleToPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=VisibleToPost
        fields=['author_url']



class CommentSerializer(serializers.ModelSerializer):
    published = serializers.DateTimeField(default=datetime.now())
    pagination_class = CommentPagination
    class Meta:
        model= Comment
        fields=['pk','comment','author','postid','published','contentType']

    def create(instance,validated_data,author,post):
        new_instance = Comment.objects.create(\
            comment=validated_data.get('comment'),\
            author=author,\
            published=timezone.now(),\
            postid=post,\
            contentType= validated_data.get('contentType')
        )
        return new_instance


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Categories
        fields=['category']

class ImageSerializer(serializers.ModelSerializer):
    img=serializers.CharField(required=False)
    class Meta:
        model=Image
        fields=['img']


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = ('follower', 'following', 'created')

    def create(self, validated_data):
        new_instance = Following.objects.create(\
            follower=validated_data.get("requester_id"),\
            following=validated_data.get("requestee_id"),\
            created=timezone.now()\
        )
        new_instance.save()

        return new_instance

class PostSerializer(serializers.ModelSerializer):
    publicationDate = serializers.DateTimeField(default=datetime.now())
    categories=CategoriesSerializer(many=True,source="post_categories",required=False)
    comments= CommentSerializer(many=True,source='post_comment',required=False)
    visibleTo=VisibleToPostSerializer(many=True,source="visible_post",required=False)
    author=AuthorSerializer(required=False)
    content=serializers.CharField(required=False)
    title=serializers.CharField(required=False,max_length=50)
    images=ImageSerializer(many=True,source="post_image",required=False)
    class Meta:
        model = Post
        fields = ['postid' ,'publicationDate','title','source' ,'origin','contentType','author','content','permission','comments','categories','unlisted','visibleTo','img']

    def create(self, validated_data,author,request):
        new_instance = Post.objects.create(content=validated_data.get('content'),title=validated_data.get('title'), permission=validated_data.get('permission'),author=author,publicationDate=datetime.now(),contentType=validated_data.get('contentType'))
        if validated_data.get('categories'):
            for category in validated_data.get('categories'):
                categories=Categories.create(post=new_instance,category=category)
        if validated_data.get('images'):
            for image in validated_data.get('images'):
                Image.objects.create(post_id=new_instance,img=image['base64'])
        if validated_data.get('permission')=='M':
            #TODO permitted authors find a way to do this
            permitted_authors=validated.get('authors')
            visible=VisibleToPost.objects.create(post=new_instance,author=author)
        if validated_data.get('permission') == 'F':
            friends=Friends.objects.filter(Q(author1=author)| Q(author2=author))
            VisibleToPost.objects.create(post=new_instance,author=author,author_url=author.url)
            for friend in friends:
                if friend.author1 == author:
                    new_visible=VisibleToPost.objects.create(post=new_instance,author=friend.author2,author_url=friend.author2.url)
                elif friend.author2 == author:
                    new_visible=VisibleToPost.objects.create(post=new_instance,author=friend.author1,author_url=friend.author1.url)
        elif validated_data.get('permission') == 'FH':
            friends=Friends.objects.filter(Q(author1=author)| Q(author2=author))
            print(friends)
            for friend in friends:
                print(friend.author2.hostName,request.get_host())
                if friend.author1 == author and friend.author2.hostName.replace("http://","") == request.get_host() and friend.author1.hostName.replace("http://","") == request.get_host():
                    print("here")
                    new_visible=VisibleToPost.objects.create(post=new_instance,author=friend.author2,author_url=friend.author2.url)
                elif friend.author2 == author and friend.author1.hostName.replace("http://","") == request.get_host() and friend.author2.hostName.replace("http://","")==request.get_host():
                    print("overhere")
                    new_visible=VisibleToPost.objects.create(post=new_instance,author=friend.author1,author_url=friend.author1.url)
        return new_instance
    

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.permission = validated_data.get('permission', instance.permission)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.save()
        return instance
    
    
