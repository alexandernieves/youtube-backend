from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Reaction, Video, Todo, Comment, History
from datetime import date


class VideoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    bonus = serializers.SerializerMethodField()
    popularity = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'youtube_link', 'user', 'username', 'created_at',
            'like_count', 'dislike_count', 'comment_count', 'bonus', 'popularity'
        ]
        extra_kwargs = {'user': {'read_only': True}}

    def get_like_count(self, obj):
        return Reaction.objects.filter(video=obj, reaction_type=Reaction.LIKE).count()

    def get_dislike_count(self, obj):
        return Reaction.objects.filter(video=obj, reaction_type=Reaction.DISLIKE).count()

    def get_comment_count(self, obj):
        return Comment.objects.filter(video=obj).count()

    def get_bonus(self, obj):
        today = date.today()
        diff = (today - obj.created_at.date()).days
        return 100 - (diff * 100)

    def get_popularity(self, obj):
        likes = self.get_like_count(obj)
        dislikes = self.get_dislike_count(obj)
        comment_count = self.get_comment_count(obj)
        bonus = self.get_bonus(obj)
        return likes * 10 - dislikes * 5 + comment_count + bonus


class HistorySerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)

    class Meta:
        model = History
        fields = ['id', 'video', 'viewed_at']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'username', 'video', 'text', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'video': {'read_only': True},
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'name', 'completed']
