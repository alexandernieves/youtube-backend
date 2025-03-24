from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

from .models import Video, Reaction, Comment, History
from .serializers import VideoSerializer, HistorySerializer


class PopularVideosTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass")

        self.video1 = Video.objects.create(
            title="Video 1",
            youtube_link="https://www.youtube.com/watch?v=abc123",
            user=self.user,
            created_at=timezone.now() - timedelta(days=1)
        )
        self.video2 = Video.objects.create(
            title="Video 2",
            youtube_link="https://www.youtube.com/watch?v=def456",
            user=self.user,
            created_at=timezone.now() - timedelta(days=2)
        )
        self.video3 = Video.objects.create(
            title="Video 3",
            youtube_link="https://www.youtube.com/watch?v=ghi789",
            user=self.user,
            created_at=timezone.now() - timedelta(days=3)
        )

        Reaction.objects.create(
            user=self.user, video=self.video1, reaction_type=Reaction.LIKE)
        Comment.objects.create(
            user=self.user, video=self.video1, text="Muy buen video!")

        Reaction.objects.create(
            user=self.user, video=self.video2, reaction_type=Reaction.DISLIKE)

    def test_popular_videos(self):
        url = reverse("popular_videos")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        for video in data:
            self.assertIn("popularity", video)


class HistoryTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="pass1")
        self.user2 = User.objects.create_user(
            username="user2", password="pass2")

        self.video = Video.objects.create(
            title="History Video",
            youtube_link="https://www.youtube.com/watch?v=history123",
            user=self.user1,
            created_at=timezone.now() - timedelta(days=1)
        )
        self.history_entry = History.objects.create(
            user=self.user1, video=self.video)
        self.history_url = reverse("get_history")

    def test_history_requires_authentication(self):
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_history_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.history_url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["video"]["id"], self.video.id)

    def test_history_is_empty_for_other_user(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.history_url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["count"], 0)
        self.assertEqual(len(data["results"]), 0)
