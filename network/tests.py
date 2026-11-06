from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Follow, Post

User = get_user_model()


class SocialTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user("alice", password="pw12345pw")
        self.b = User.objects.create_user("bob", password="pw12345pw")

    def test_signup_creates_profile(self):
        r = self.client.post(reverse("signup"), {"username": "newbie", "password1": "Str0ngPass!9", "password2": "Str0ngPass!9"})
        self.assertRedirects(r, reverse("home"))
        self.assertTrue(User.objects.get(username="newbie").profile)

    def test_post_comment_like(self):
        self.client.login(username="alice", password="pw12345pw")
        self.client.post(reverse("post_create"), {"content": "hi"})
        post = Post.objects.get()
        self.client.post(reverse("comment_add", args=[post.pk]), {"content": "nice"})
        self.assertEqual(Comment.objects.count(), 1)
        r = self.client.post(reverse("post_like", args=[post.pk]))
        self.assertEqual(r.json(), {"liked": True, "count": 1})
        r = self.client.post(reverse("post_like", args=[post.pk]))
        self.assertEqual(r.json(), {"liked": False, "count": 0})

    def test_follow_toggle_and_self_follow(self):
        self.client.login(username="alice", password="pw12345pw")
        r = self.client.post(reverse("follow", args=["bob"]))
        self.assertEqual(r.json(), {"following": True, "followers": 1})
        self.assertEqual(self.client.post(reverse("follow", args=["alice"])).status_code, 400)
        r = self.client.post(reverse("follow", args=["bob"]))
        self.assertEqual(r.json()["following"], False)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Follow.objects.create(follower=self.a, following=self.a)

    def test_login_required_and_permissions(self):
        post = Post.objects.create(author=self.a, content="x")
        self.assertEqual(self.client.post(reverse("post_like", args=[post.pk])).status_code, 401)
        self.client.login(username="bob", password="pw12345pw")
        self.assertEqual(self.client.post(reverse("post_delete", args=[post.pk])).status_code, 403)

    def test_pages_render(self):
        Post.objects.create(author=self.a, content="x")
        for name, args in [("home", []), ("people", []), ("profile", ["alice"]), ("login", []), ("signup", [])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)
        self.client.login(username="alice", password="pw12345pw")
        for name in ["home", "people", "profile_edit"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("post_detail", args=[Post.objects.get().pk])).status_code, 200)
