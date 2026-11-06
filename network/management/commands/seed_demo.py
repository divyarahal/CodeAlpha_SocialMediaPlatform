from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from network.models import Comment, Follow, Post

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo users (password: demo12345), posts, comments, likes and follows."

    def handle(self, *args, **opts):
        users = {}
        for name, bio, loc in [
            ("alice", "Coffee, code and cats.", "Delhi"),
            ("bob", "Cricket fan. Part-time developer.", "Mumbai"),
            ("carol", "Reading one book a week.", "Noida"),
        ]:
            u, created = User.objects.get_or_create(username=name)
            if created:
                u.set_password("demo12345")
                u.save()
            u.profile.bio, u.profile.location = bio, loc
            u.profile.save()
            users[name] = u
        if not Post.objects.exists():
            p1 = Post.objects.create(author=users["alice"], content="Hello Connectly! First post here ☕")
            p2 = Post.objects.create(author=users["bob"], content="Django makes building apps so fast.")
            p3 = Post.objects.create(author=users["carol"], content="Finished a great book today. Recommendations welcome!")
            p1.likes.add(users["bob"], users["carol"])
            p2.likes.add(users["alice"])
            Comment.objects.create(post=p1, author=users["bob"], content="Welcome, Alice!")
            Comment.objects.create(post=p3, author=users["alice"], content="Try 'Atomic Habits'.")
        for a, b in [("alice", "bob"), ("bob", "alice"), ("carol", "alice")]:
            Follow.objects.get_or_create(follower=users[a], following=users[b])
        self.stdout.write(self.style.SUCCESS("Demo data ready. Log in as alice / bob / carol with password demo12345"))
