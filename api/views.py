from api.models import Author, FriendRequest, Friends,Post,Comment,VisibleToPost, Following,Node
from api.serializers import AuthorSerializer, FriendRequestSerializer, FriendsSerializer,PostSerializer,CommentSerializer,VisibleToPostSerializer,CategoriesSerializer, FollowingSerializer
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.utils.timezone import get_current_timezone, make_aware
from django.core import serializers
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from django.core.serializers.json import DjangoJSONEncoder
import sys
from django.http import JsonResponse
from django.db.models import Q
from django.core import serializers
from .pagination import CustomPagination,CommentPagination
from rest_framework.settings import api_settings
import json
from django.utils import timezone
import requests

class ListAuthors(APIView):
    """
    API View to list all authors in the system
    Requires token authentication.
    """

    #permission_classes = (IsAuthenticated,)
    serializer_class=AuthorSerializer

    def post(self,request,format=None):
        authors_to_pass=[]
        users_search = JSONParser().parse(request)
        print("**********************************************************************")
        print(users_search['users_search'])
        users_username=users_search['userName']
        users_search=users_search['users_search']
        if users_search is not "":
            test  =Friends.objects.all()
            print("here she is")
            #if(test):
            #    print(test[0].author1)
            #print(queryset)
            queryset=Author.objects.filter(Q(userName__startswith=users_search))
            print("1")
            searcher = Author.objects.filter(Q(userName=users_username))
            print("1")
            print(users_username)
            pple_to_follow = FriendRequest.objects.filter(Q(from_author=searcher[0]) | Q(to_author=searcher[0]))
            print("here is the searcher")
            print(searcher[0])
            #queryset = queryset.filter(userName=users_search['users_search']).values_list('userName',flat=True)
            print("**********************************************************************")
            print("**********************************************************************")
            print("**********************************************************************")
            print("**********************************************************************")
            """ for q in queryset:
                author = Author.objects.get(userName=q)
                print("here is the serializer")
                serializer = AuthorSerializer(author)
                print(serializer.data) """
            print("here is the query set")
            print(queryset)
            print(pple_to_follow)

            try:
                for q in queryset:
                    print(q)
                    author = Author.objects.get(userName=q)

                    serializer = AuthorSerializer(author)
                    print(serializer.data)
                    authors_to_pass.append(serializer.data)
            except IndexError:
                pass

            index_to_pop=[]

            for i in range(len(authors_to_pass)):
                try:
                    for p in pple_to_follow:
                        print("asfasfff")
                        print(type(p.from_author.userName))
                        print(type(authors_to_pass[i]['userName']))
                        if(p.from_author.userName==authors_to_pass[i]['userName'] or p.to_author.userName==authors_to_pass[i]['userName']):
                            index_to_pop.append(i)
                except AttributeError:
                    print("Attribute error...but should continue")

            for i in reversed(index_to_pop):
                authors_to_pass.pop(i)
            print(authors_to_pass)







            return Response(authors_to_pass)


    def get(self,request):
        authors=Author.objects.all().order_by('-pk')
        serializer = AuthorSerializer(authors,many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        return {"request": self.request}


@api_view(['POST'])
def notifications(request):

    if request.method != 'POST':
        # invalid method
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    print("@@@@@@@@@@@@@@@@@")
    print(data)
    requester_id = data.get('from_author')


    try:
        author_object = FriendRequest.objects.filter(Q(to_author=requester_id) & Q(accepted=False) & Q(regected=False))
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(requester_id)
        #print(author_object[0])
        #searcher = Author.objects.filter(Q(userName=users_username))

        author_list=[]

        for a in author_object:
            print(a.from_author)
            follower = Author.objects.get(userName=a.from_author)
            serializer = AuthorSerializer(follower)
            author_list.append(serializer.data)




    except FriendRequest.DoesNotExist:
        print("Error;friend filter didn't work")
    print("*^*&^*&**^*^^*&^&*^*^&*^()*&)(&*(*&()&)(&)(*&)(*&")
    print(author_list)
    return Response(author_list)



class AuthorDetails(APIView):
    """
    API view to show details of specified author
    Requires token authentication.
    """
    #permission_classes = (IsAuthenticated,)
    def get_author(self,request,pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return "error"
        return author

    def get(self, request, pk, format=None):
        """Returns author <id=pk> details.
        """
        author=self.get_author(request,pk)
        if author=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find author"},status=status.HTTP_200_OK)
        serializer = AuthorSerializer(author,context={'request':request})
        return Response(serializer.data)

    def put(self, request,pk, format=None):
        """Updates author details if he/she is an authenticated user.
        """
        author=self.get_author(request,pk)
        if author=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find author"},status=status.HTTP_200_OK)
        if pk == str(author.pk):
            data= JSONParser().parse(request)
            serializer = AuthorSerializer(Author, data=data)
            if serializer.is_valid():
                serializer.update(author,data)
                return Response({"query":"Update Author Details","success":True,"message":"Updated Information"},status=status.HTTP_200_OK)
            return Response({"query":"Update Author Details","success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"query":"Update Author Details","success":False, "message":"this is not your profile"}, status=status.HTTP_400_BAD_REQUEST)


class PostOfAuth(APIView):
    """
    API view to list all posts visible to authenticated user
    Requires token authentication.
    """
    paginator= CustomPagination()
    permission_classes = (IsAuthenticated,)
    def get_author(self,request):
        try:
            author=Author.objects.get(owner=request.user)
        except Author.DoesNotExist:
            return "error"
        return author


    def get(self,request,format=None):
        search=request.GET.get('author','')
        if search!= '':
            self.get_posts_for_remote(request,search)
        else:
            author=self.get_author(request)
            if author=="error":
                return Response({"query":"posts","success":False,"message":"Cannot find author"},status=status.HTTP_404_NOT_FOUND)
            visiblePosts=VisibleToPost.objects.filter(Q(author_url=author.url)| Q(author=author)).values('post_id')
            if not visiblePosts:
                return Response({"query":"posts","success":True,"message":"No posts visible to you"},status=status.HTTP_200_OK)
            posts=[]
            for post in visiblePosts:
                v_posts=Post.objects.filter(Q(postid=post['post_id'])).order_by('publicationDate')
                page = self.paginator.paginate_queryset(v_posts,request)
                serializer=PostSerializer(page,many=True)
                posts.append(serializer.data)
            return self.paginator.get_paginated_response(posts,'posts')


    def get_serializer_context(self):
        return {"request": self.request}


    def post(self,request,format=None):
        author=self.get_author(request)
        if author=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find author"},status=status.HTTP_200_OK)
        data=JSONParser().parse(request)
        print(data)
        serializer=PostSerializer(Post,data=data)
        if serializer.is_valid():
            serializer.create(data,author)
            return Response({"query":"Add Post", "success":True ,"message":"Added a New Post"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    def get_posts_for_remote(self,request,search):
        ## getting the remote user node to see if shareposts or shareimages is set 
        node=Node.objects.get(user=request.user)
        ## finding friends of the specific remote user that is authenticated
        friends=Friends.objects.filter(Q(author2_url=search)).values_list('author1')
        myfriends=list(friends)
        ## checking the visible to table to check if there are additional posts visible to user
        filterposts=[]
        ## getting all posts of those friends found above
        for friend in myfriends:
            post=Post.objects.filter(Q(author=friend)).order_by('publicationDate')
            #filtering posts to check if server admin denies access to images
            if node.shareImages==False:
                if post.values('contentType')[0]['contentType']=="image/png;base64" or post.values('contentType')[0]['contentType']=="image/jpeg;base64":
                    pass
                else:
                    page = self.paginator.paginate_queryset(post,request)
                    serializer=PostSerializer(page,many=True)
                    filterposts.append(serializer.data)
            else:
                page = self.paginator.paginate_queryset(post,request)
                serializer=PostSerializer(page,many=True)
                filterposts.append(serializer.data)
        #getting permitted posts visible to remote author
        visiblePosts=VisibleToPost.objects.filter(Q(author_url=search)).values('post_id')
        for post in visiblePosts:
            v_posts=Post.objects.filter(Q(postid=post['post_id'])).order_by('publicationDate')
            if not node.shareImages==False:
                if v_posts.values('contentType')[0]['contentType']!="image/png;base64" or v_posts.values('contentType')[0]['contentType']!="image/jpeg;base64":
                     pass
                else:
                    page = self.paginator.paginate_queryset(v_posts,request)
                    serializer=PostSerializer(page,many=True)
                    filterposts.append(serializer.data)
            else:
                page = self.paginator.paginate_queryset(v_posts,request)
                serializer=PostSerializer(page,many=True)
                filterposts.append(serializer.data)
        ## if server admin regects sharing posts
        if not node.sharePosts:
            return Response({"message":"Server Denied your Request"},status=status.HTTP_401_UNAUTHORIZED)
        if filterposts:
            return self.paginator.get_paginated_response(serializer.data,'posts')
        else:
            return Response({"query":"posts","success":True,"message":"No posts visible to you"},status=status.HTTP_200_OK)
    
    #TODO find friends of friends so that we can send foaf posts to remote server
    # def find_foaf(self,friends,search):
    #     FOAFList=[]
    #     for friend in friends: 
    #         otherfriendList=[]
    #         otherfriends= Friends.objects.filter(Q(author_1=friend)| Q(author_2=friend))
    #         for foaf in otherfriends:
    #             if foaf.author1 == friend and foaf.author2_url!=search:
    #                 FOAFList.append(author2)
    #             elif foaf.author2== fr and foaf.author1_url!=search:
    #                 FOAFList.append(friend.author1)
    #     return FOAFList
            
        

class PublicPosts(APIView):
    """
    API view to list all public posts
    Requires token authentication.
    """

    #permission_classes = (IsAuthenticated,)
    paginator= CustomPagination()
    def get(self, request,format=None):
        post = Post.objects.all().filter(permission="P")
        page=self.paginator.paginate_queryset(post,request)
        serializer = PostSerializer(page,many=True)
        return self.paginator.get_paginated_response(serializer.data,'posts')

class ProfileOfAuth(APIView):
    """
    API view to see profile of auth
    """

    #permission_classes = (IsAuthenticated,)
    def get(self, request,format=None):
        author = Author.objects.get(owner=request.user)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)




class PostOfAuthors(APIView):
    """
    API view to list post of a certain author visble to authenticated user
    Requires token authentication.
    Only GET IS ALLOWED HERE
    """
    paginator= CustomPagination()
    # permission_classes = (IsAuthenticated,)
    def get_author(self,query):
        print(query)
        try:
            author=Author.objects.get(author_id=query)
        except Author.DoesNotExist:
            return "error"
        return author

    def get(self, request,pk,format=None):
        search=request.GET.get('author','')
        author=self.get_author(pk)
        ##To do filter post based on sharePosts and shareImages
        if search:
            node=Node.objects.get(owner=request.user)
        posts=[]
        if author=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find author"},status=status.HTTP_200_OK)
        #This code block is for finding posts of pk author visble to remote user
        if search:
            are_friends= Friends.objects.filter(Q(author1=author)& Q(author2_url=search)| Q(author1_url=search) & Q(author2=author))
            if are_friends:
                post=Post.objects.filter(Q(permission="F")& Q(author=author)).order_by("-publicationDate")
                page=self.paginator.paginate_queryset(post,request)
                serializer=PostSerializer(page,many=True)
                posts.append(serializer.data)
            visible_posts=VisibleToPost.objects.filter(Q(author_url=search)).values('post')
            for post in visible_posts:
                visible_post=Post.objects.filter(Q(postid=post['post']))
                page=self.paginator.paginate_queryset(visible_post,request)
                serializer=PostSerializer(page,many=True)
                posts.append(serializer.data)
            #todo check if friend of friend and return those posts
        #This code block is for finding posts of author visble to local user
        else:
            other_auth=Author.objects.get(owner=request.user)
            are_friends= Friends.objects.filter(Q(author1=author)& Q(author2=other_auth)| Q(author1=other_auth) & Q(author2=author))
            if are_friends:
               Posts.objects.filter(Q(permission="F")& Q(author=author)).order_by("-publicationDate")
               page=self.paginator.paginate_queryset(post,request)
               serializer=PostSerializer(page,many=True)
               posts.append(serializer.data)
            visble_posts=VisibleToPost.objects.filter(Q(author=other_auth))
            for post in visble_posts:
                visible_post=Posts.objects.filter(Q(postid=post))
                page=self.paginator.paginate_queryset(post,request)
                serializer=PostSerializer(page,many=True)
                posts.append(serializer.data)
            #todo check if friend of friend and return those posts
        if not posts:
            return Response({"query":"posts","success":True,"message":"Sorry No Posts Visible to You"},status=status.HTTP_200_OK)
        else:
            return self.paginator.get_paginated_response(posts,'posts')

    


class PostDetails(APIView):
    """
    API view give you details of a specific post given by id
    Requires token authentication.

    GET PUT DELETE OPERATIONS ALLOWED HERE
    """
    def get_author(self,request):
        try:
            author=Author.objects.get(owner=request.user)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return author

    def get_post(self,pk):
        try:
            post=Post.objects.get(postid=pk)
        except Post.DoesNotExist:
            return "error"
        return post

    def get(self, request,pk,format=None):
        post=self.get_post(pk)
        if post=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find post"},status=status.HTTP_200_OK)
        else:
            serializer=PostSerializer(post)
            return Response({"query":"posts","success":True,"posts":serializer.data},status=status.HTTP_200_OK)

    def put(self,request,pk,format=None):
        if(Node.objects.get(user=request.user)):
            return Response({"message":"sorry you do not have access to this"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            author= self.get_author(request)
            post=self.get_post(pk)
            if post=="error":
                return Response({"query":"posts","success":False,"message":"Cannot find post"},status=status.HTTP_200_OK)
            if author == post.author:
                data=JSONParser().parse(request)
                serializer = PostSerializer(post,data=data)
                if serializer.is_valid():
                    serializer.update(post,data)
                    return Response({"query":"Update Users Post","success":True, "message":"Updated your post"},status=status.HTTP_200_OK)
                return Response({"query":"Update Users Post","success":False, "message":serializer.errors},status=status.HTTP_200_OK)
            else:
                return Response({"query":"Update Users Post","success":False, "message":"Sorry this is not your post to update"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,format=None):
        if(Node.objects.get(user=request.user)):
            return Response({"message":"sorry you do not have access to this action"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            author=self.get_author(request)
            post=self.get_post(pk)
            if author==post.author:
                post.delete()
                return Response({"query":"Delete Users Post","success":True, "message":"Deleted your post"},status=status.HTTP_200_OK)
            else:
                return Response({"query":"Delete Users Post","success":False, "message":"Sorry this is not your post to delete"}, status=status.HTTP_400_BAD_REQUEST)


class PostComments(APIView):
    """
    API view give you details of a specific post given by id
    Requires token authentication.

    GET PUT DELETE OPERATIONS ALLOWED HERE
    """
    paginator= CommentPagination()
    def get_author(self,request):
        try:
            author=Author.objects.get(owner=request.user)
        except Author.DoesNotExist:
            return "error"
        return author

    def get_comment(self,post):
        return Comment.objects.filter(postid=post)

    def get_post(self,pk):
        try:
            post=Post.objects.get(postid=pk)
        except Post.DoesNotExist:
            return "error"
        return post

    def get(self, request,pk,format=None):
        post=self.get_post(pk)
        if post=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find post"},status=status.HTTP_404_NOT_FOUND)
        else:
            comments=self.get_comment(post)
            page=self.paginator.paginate_queryset(comments,request)
            serializer=CommentSerializer(comments,many=True)
            return self.paginator.get_paginated_response(serializer.data,'comment')

    def post(self,request,pk,format=None):
        data=JSONParser().parse(request)
        post=self.get_post(pk)
        if post=="error":
            return Response({"query":"posts","success":False,"message":"Cannot find post"},status=status.HTTP_404_NOT_FOUND)
        try:
            node=Node.objects.get(user=request.user)
            if node:
                if self.remote_can_comment(node,post,data):
                    #TODO find a better method to do this
                    author=Author.objects.create(url=data['url'],owner=request.user,userName="remote_user")
                else:
                    return Response({"message":"sorry you cannot comment on this post"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Node.DoesNotExist:
            author=self.get_author(request) 
        serializer=CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.create(data,author,post)
            return Response({"query":"Create Comment", "success":True ,"message":"Comment Created"}, status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def remote_can_comment(self,node,post,data):
        friends=Friends.objects.filter(Q(author1=post.author)& Q(author2_url=data['url'])|Q(author2=post.author)& Q(author1_url=data['url']))
        if post.permission=="F" and friends:
            return True
        elif post.permission=="L":
            visiblePosts=VisibleToPost.objects.filter(Q(author_url=data['url']) & Q(post=post))
            if visiblePosts:
                return True
            return False
        elif post.permission=="P":
            return True
        # Todo checking if there are friends of friends so that you can allow them to comment
        # elif post.permission=="FF" and friends:
        #     set=()
        #     for friend in friends:
        else:
            return False


@api_view(['POST'])
def send_friend_request(request):

    if request.method != 'POST':
        # invalid method
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # insert new entry in database
    data = JSONParser().parse(request)
    remote=False
    if data.get('query')=='friendrequest':
        requester_id = data.get('author').id
        requestee_id = data.get('friend').id
        requester_id=requester_id.split('/')[-1]
        requestee_id=requestee_id.split('/')[-1]
        remote=True
    else:
        requester_id = data.get('from_author')
        requestee_id = data.get('to_author')

    # TODO remote part
    # decomment it later
    # friend_request_to_remote(data)

    """ if yes make friends"""
    try:
        existing_request = FriendRequest.objects.get(to_author=requester_id, from_author=requestee_id)
        """make them friends"""
        requester = Author.objects.get(pk=requester_id)
        requestee = Author.objects.get(pk=requestee_id)
        temp_dict = {"requester" :requester , "requestee":requestee}
        enroll_following(temp_dict)
        return make_them_friends(requester_id, requestee_id, existing_request)
    except FriendRequest.DoesNotExist:
        pass
    except FriendRequest.MultipleObjectsReturned:
        print("Error: duplicate instances in DB", file=sys.stderr)

    """ check duplicate requests"""
    try:
        existing_request = FriendRequest.objects.filter(Q(from_author=requester_id) & Q(to_author=requestee_id)).exists()
        if existing_request:
            return Response(status=status.HTTP_201_CREATED)
    except FriendRequest.DoesNotExist:
        pass
    except FriendRequest.MultipleObjectsReturned:
        print("Error: duplicate instances in DB", file=sys.stderr)

    """fresh request, implement it"""
    serializer = FriendRequestSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        response = Response(serializer.data)
    else:
        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if remote:
        try:
            requester = Author.objects.get(pk=requester_id)
        except AuthorDoesNotExist:
            pass
        try:
            requestee = Author.objects.get(pk=requestee_id)
        except AuthorDoesNotExist:
            pass
        if not requester:
            requester_info=requests.get(data.get('author').url)
            json_data = json.loads(requester.text)
            requester=Author.object.create(url=json_data['url'],userName=json_data['displayName'],hostName=json_data['host'])
        if not requestee:
            requestee_info=request.get(data.get('friend').url)
            json_data = json.loads(requester.text)
            requestee=Author.object.create(url=json_data['url'],userName=json_data['displayName'],hostName=json_data['host'])
    else:
        requester = Author.objects.get(pk=requester_id)
        requestee = Author.objects.get(pk=requestee_id)
    temp_dict = {"requester" :requester , "requestee":requestee}
    enroll_following(temp_dict)

    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def respond_to_friend_request(request):
    """ modify friend request entry values (accept and reject)"""
    if request.method != 'POST':
        # invalid method
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    try:
        req = FriendRequest.objects.filter(Q(from_author=data.get("from_author")) & Q(to_author=data.get("to_author")))
    except FriendRequest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if data.get("accepted"):
        requester_id = data.get("from_author")
        requestee_id = data.get("to_author")

        existing_request = FriendRequest.objects.get(to_author=requestee_id, from_author=requester_id)
        """make them friends"""
        requester = Author.objects.get(pk=requester_id)
        requestee = Author.objects.get(pk=requestee_id)
        temp_dict = {"requester" :requestee , "requestee":requester}
        #enroll_following(temp_dict)
        make_them_friends(requester_id, requestee_id, existing_request)
        print("came asfasdfsa")
        return Response(status=status.HTTP_200_OK)

    temp_dict = {"from_author" :data.get("from_author") , "to_author":data.get("to_author"), "accepted":data.get("accepted") , "regected":data.get("regected")}
    serializer = FriendRequestSerializer(FriendRequest,data=temp_dict)
    if serializer.is_valid():
        for q in req:
            serializer.update(q,temp_dict)
        return Response(status=status.HTTP_200_OK)
    """ TODO user would get notification about requests are not rejected"""

@api_view(['POST'])
def unfriend(request):
    if request.method != 'POST':
        # invalid method
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """ TODO: 1, remove from friend list | 2, remove from following list"""
    # delete from friend list
    data = JSONParser().parse(request)
    # print("???????????????????????????", data.get("requester"))
    requester = Author.objects.get(pk=data.get("from_author"))
    requestee = Author.objects.get(pk=data.get("to_author"))

    try:
        req = Friends.objects.filter(Q(author1=requester , author2=requestee) | Q(author1=requestee , author2=requester))
        for q in req:
            q.delete()
    except FriendRequest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    req = Following.objects.filter(follower=requester, following=requestee)
    if req.exists():
        req.delete()
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # try:
    # except FriendRequest.DoesNotExist:
    #     raise
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # temp_dict = {"follower" :a1 , "following":a2}
    # unfollow(temp_dict)

    # if not unfollow(pk, following):
    #     print("Error: following instance is not found", file=sys.stderr)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def get_friends(request, authorid):
    current_user_id = authorid;

    try:
        current_user = Author.objects.get(pk=authorid)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    friends_queryset = Friends.objects.filter(Q(author1=current_user) | Q(author2=current_user))
    friends_list = []

    for friend in friends_queryset:
        if current_user.pk == friend.author1.pk:
            friends_list.append(friend.author2.author_id)
        else:
            friends_list.append(friend.author1.author_id)
    return Response({"query":"Friends","authors":friends_list},status=status.HTTP_200_OK)

@api_view(['GET'])
def check_friendship(request, authorid, authorid2):
    try:
        user1 = Author.objects.get(pk=authorid)
        user2 = Author.objects.get(pk=authorid2)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    friends_queryset = Friends.objects.filter(Q(author1=user1, author2=user2) | Q(author1=user2, author2=user1))
    friends_list = []
    friends_list.append(user1.author_id)
    friends_list.append(user2.author_id)
    friends = friends_queryset.exists()

    return Response({"query":"Friends","authors":friends_list, "friends": friends},status=status.HTTP_200_OK)

@api_view(['GET'])
def get_friends_local(request):
    pass


"""some ideas about friends of friends: """
""" create friend list for each author, make them set, and then count intersection of them"""

"""***************************Utility*************************"""
def make_them_friends(author_one, author_two, existing_request):
    # change status of a friend request
    existing_request.accepted = True
    existing_request.regected = False
    temp_dict = {"from_author" :existing_request.from_author , "to_author":existing_request.to_author}
    # create instance of Friends
    serializer = FriendsSerializer(data=temp_dict)
    serializer.create(temp_dict)
    #existing_request.delete()
    temp_dict2 = {"from_author" :existing_request.from_author , "to_author":existing_request.to_author,"accepted" :existing_request.accepted , "regected":existing_request.regected}

    serializer2 = FriendRequestSerializer(data=temp_dict2)
    serializer2.update(existing_request,temp_dict2)




    if serializer.is_valid():
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def enroll_following(validated_data):
    """TODO check duplicate here"""
    instance = Following.objects.filter(follower=validated_data.get("requester"), following=validated_data.get("requestee"))
    if instance.exists():
        return Response(status=status.HTTP_200_OK)
    # serializer = FollowingSerializer(data=validated_data)
    # serializer.create(validated_data)
    new_instance = Following.objects.create(\
        follower=validated_data.get("requester"),\
        following=validated_data.get("requestee"),\
        created=timezone.now()\
    )
    new_instance.save()

    return Response(status=status.HTTP_200_OK)
    # if serializer.is_valid():
    #     return Response(serializer.data)
    # else:
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def unfollow(validated_data):
    try:
        req = Following.objects.get(follower=validated_data.get("follower"), following=validated_data.get("following"))
    except Following.DoesNotExist:
        return False
    req.delete()
    return True

def friend_request_to_remote(dict_data):
    # get author
    # check hostname
    # if remote
    # send request to remote
    # get response

    author_id = dict_data.get("from_author")
    friend_id = dict_data.get("to_author")

    author_obj = Author.objects.get(pk=author_id)
    friend_obj = Author.objects.get(pk=friend_id)

    """
    id, host, displayName, url
    """
    author_dict = {"id": author_obj.author_id,"host": author_obj.hostName, "displayName": author_obj.userName, "url": author_obj.url}
    friend_dict = {"id": friend_obj.author_id,"host": friend_obj.hostName, "displayName": friend_obj.userName, "url": friend_obj.url}
    full_object = {"query":"friendrequest", "author": author_dict, "friend":friend_dict}

    j_data = json.dumps(full_object, cls=DjangoJSONEncoder)
    # TODO adpat URL to practical url
    r = requests.post(url="https://project-cmput404.herokuapp.com/api/friendRequest", data=j_data)

    return r








#
