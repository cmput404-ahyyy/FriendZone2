from django.contrib import admin
from .models import Author, FriendRequest,Friends,Post, Comment,VisibleToPost,Categories, Following,Node,Image
# Register your models here.
admin.site.register(Author)
admin.site.register(FriendRequest)
admin.site.register(Friends)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(VisibleToPost)
admin.site.register(Categories)
admin.site.register(Following)
admin.site.register(Image)
admin.site.register(Node)
