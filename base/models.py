from django.db import models
from django.contrib.auth.models import User


class History(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='history')
    video = models.ForeignKey('Video', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} vio {self.video.title} a las {self.viewed_at}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey('Video', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.text[:30]}..."


class Video(models.Model):
    title = models.CharField(max_length=255)
    youtube_link = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=7, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} -> {self.video.title} ({self.reaction_type})"


class Todo(models.Model):
    name = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='todo')

    def __str__(self):
        return self.name
