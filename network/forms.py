from django import forms
from .models import Comment, Post, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        widgets = {"content": forms.Textarea(attrs={"rows": 3, "maxlength": 280, "placeholder": "What's happening?"})}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {"content": forms.TextInput(attrs={"maxlength": 280, "placeholder": "Write a comment…"})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "location"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3, "maxlength": 300})}
