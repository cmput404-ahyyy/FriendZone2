from django.urls import path,include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .api import RegisterAPI,LoginAPI,UserAPI
from knox import views as knox_views
from .views import ListAuthors,AuthorDetails,PostOfAuth,PublicPosts,PostOfAuthors,PostDetails,PostComments,ProfileOfAuth,FriendRequest

urlpatterns = [
    #Just retrieves list of authors in the database
    path('/auth/',include('knox.urls')),
    #for registering a user route
    path('auth/register',RegisterAPI.as_view(), name='signup'),

    # for logining in a user route
    path('auth/login',LoginAPI.as_view(), name='login'),

    path('auth/user',UserAPI.as_view(), name='user'),

    path('auth/logout',knox_views.LogoutView.as_view(),name='knox_logout'),

    path('authors/', ListAuthors.as_view(), name='authors_list'),
    #Retrieves this specific authors details
    path('authors/<pk>/', AuthorDetails.as_view(),name='author'),

    path('author/posts/',PostOfAuth.as_view(), name="auth_posts"),

    path('author/profile/',ProfileOfAuth.as_view(),name='author'),

    path('notifications/', views.notifications, name="notifications"),


    #All posts marked as public on the server
    path('posts/',PublicPosts.as_view(), name='posts'),
    #All posts made by this specific author, visible to authenticated user
    path('author/<pk>/posts/', PostOfAuthors.as_view(), name='author_posts'),
    #Just retrieves a single post with that id
    path('posts/<pk>/',PostDetails.as_view(), name="post_info"),
    #Just retrieves comments to that specific post
    path('posts/<pk>/comments/',PostComments.as_view(), name="post_comments"),
    #Just sends a friend request
    path('friendRequest/',views.send_friend_request, name="friend_request"),
    # result of a friend request
    path('friendResult/', views.respond_to_friend_request, name="respond_frequest"),
    # Just un-befriend(unfollow) an author
    path('unfriend/', views.unfriend, name="unbefriend"),
    # # Get all my friends
    # path('friends/', views.get_friends, name="get"),
    # Get all my friends
    path('local_friends/', views.get_friends_local),
    # Get all my friends
    path('authors/<authorid>/friends/', views.get_friends, name="get_global_friends"),
    # Get all my friends
    path('authors/<authorid>/local_friends/', views.get_friends, name="get_local_friends"),
    # Ask if 2 authors are friends
    path('author/<authorid>/friends/<authorid2>/', views.check_friendship, name='friendship')
]
