from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("people/", views.people, name="people"),
    path("post/new/", views.create_post, name="post_create"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/delete/", views.delete_post, name="post_delete"),
    path("post/<int:pk>/like/", views.toggle_like, name="post_like"),
    path("post/<int:pk>/comment/", views.add_comment, name="comment_add"),
    path("settings/profile/", views.edit_profile, name="profile_edit"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/follow/", views.toggle_follow, name="follow"),
]
