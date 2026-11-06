from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileForm
from .models import Comment, Follow, Post

User = get_user_model()


def _posts():
    return (
        Post.objects.select_related("author", "author__profile")
        .annotate(like_count=Count("likes", distinct=True), comment_count=Count("comments", distinct=True))
        .order_by("-created_at")
    )


def _mark_liked(posts, user):
    posts = list(posts)
    liked = set()
    if user.is_authenticated and posts:
        liked = set(user.liked_posts.filter(id__in=[p.id for p in posts]).values_list("id", flat=True))
    for p in posts:
        p.liked = p.id in liked
    return posts


def _paginate(request, queryset, per_page=10):
    page = Paginator(queryset, per_page).get_page(request.GET.get("page"))
    page.object_list = _mark_liked(page.object_list, request.user)
    return page


def _following_ids(user):
    if not user.is_authenticated:
        return set()
    return set(Follow.objects.filter(follower=user).values_list("following_id", flat=True))


def home(request):
    feed = request.GET.get("feed", "following" if request.user.is_authenticated else "all")
    posts = _posts()
    if feed == "following" and request.user.is_authenticated:
        ids = _following_ids(request.user) | {request.user.id}
        posts = posts.filter(author_id__in=ids)
    else:
        feed = "all"
    return render(request, "network/home.html", {
        "page_obj": _paginate(request, posts), "feed": feed, "form": PostForm(),
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to Connectly!")
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
    else:
        messages.error(request, "Post must be 1–280 characters.")
    return redirect(request.POST.get("next") or "home")


def post_detail(request, pk):
    post = get_object_or_404(_posts(), pk=pk)
    post.liked = request.user.is_authenticated and post.likes.filter(pk=request.user.pk).exists()
    comments = post.comments.select_related("author")
    return render(request, "network/post_detail.html", {"post": post, "comments": comments, "form": CommentForm()})


@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You can only delete your own posts.")
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect(request.POST.get("next") or "home")


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(post=post, author=request.user, content=form.cleaned_data["content"])
    else:
        messages.error(request, "Comment must be 1–280 characters.")
    return redirect("post_detail", pk=pk)


@require_POST
def toggle_like(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({"liked": liked, "count": post.likes.count()})


def profile(request, username):
    owner = get_object_or_404(User.objects.select_related("profile"), username=username)
    posts = _posts().filter(author=owner)
    return render(request, "network/profile.html", {
        "owner": owner,
        "page_obj": _paginate(request, posts),
        "followers": owner.follower_set.count(),
        "following": owner.following_set.count(),
        "post_total": owner.posts.count(),
        "is_following": owner.id in _following_ids(request.user),
    })


@require_POST
def toggle_follow(request, username):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({"error": "You can't follow yourself."}, status=400)
    rel, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        rel.delete()
    return JsonResponse({"following": created, "followers": target.follower_set.count()})


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("profile", username=request.user.username)
    return render(request, "network/profile_edit.html", {"form": form})


def people(request):
    q = request.GET.get("q", "").strip()
    users = User.objects.select_related("profile").annotate(follower_total=Count("follower_set")).order_by("-follower_total", "username")
    if request.user.is_authenticated:
        users = users.exclude(pk=request.user.pk)
    if q:
        users = users.filter(Q(username__icontains=q) | Q(profile__bio__icontains=q))
    users = list(users[:50])
    following_ids = _following_ids(request.user)
    for u in users:
        u.is_following = u.id in following_ids
    return render(request, "network/people.html", {"users": users, "q": q})
