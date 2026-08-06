from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User
# from django.db.models.deletion import CASCADE

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Hub(models.Model):
    """Community-like construct (similar to subreddit)."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, default="hub.svg")
    followers = models.ManyToManyField('User', related_name='followed_hubs', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    hub = models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    upvoted_by = models.ManyToManyField(User, related_name='upvoted_messages', blank=True)
    downvoted_by = models.ManyToManyField(User, related_name='downvoted_messages', blank=True)
    is_flagged = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=200, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    @property
    def score(self):
        return self.upvoted_by.count() - self.downvoted_by.count()

    @property
    def visible_replies(self):
        return self.replies.filter(is_removed=False)

    def __str__(self):
        return self.body[0:50]