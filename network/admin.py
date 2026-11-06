from django.contrib import admin
from .models import Comment, Follow, Post, Profile

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follow)
