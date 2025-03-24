from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.views import APIView
from datetime import date
import random

from .models import Todo, Video, Reaction, Comment, History
from .serializers import (
    TodoSerializer,
    UserRegisterSerializer,
    UserSerializer,
    VideoSerializer,
    CommentSerializer,
    HistorySerializer,
)


from rest_framework.pagination import PageNumberPagination


class HistoryPagination(PageNumberPagination):
    page_size = 10


class RegisterViewHistory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        video_id = request.data.get("video_id")
        if not video_id:
            return Response({"error": "video_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        history, created = History.objects.get_or_create(
            user=request.user, video=video)
        history.save()
        serializer = HistorySerializer(history)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    history_qs = History.objects.filter(
        user=request.user).order_by('-viewed_at')
    paginator = HistoryPagination()
    result_page = paginator.paginate_queryset(history_qs, request)
    serializer = HistorySerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_to_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({"error": "Video no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    reaction_type = request.data.get('reaction_type')
    if reaction_type not in ['like', 'dislike']:
        return Response({"error": "reaction_type debe ser 'like' o 'dislike'."}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    reaction, created = Reaction.objects.get_or_create(user=user, video=video)
    reaction.reaction_type = reaction_type
    reaction.save()

    serializer = VideoSerializer(video)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_videos(request):
    videos = Video.objects.all().order_by('-created_at')
    serializer = VideoSerializer(videos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_video_detail(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({"error": "Video no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VideoSerializer(video)
    return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("CustomTokenObtainPairView -> POST data:", request.data)
        response = super().post(request, *args, **kwargs)
        print("Login response data:", response.data)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("CustomTokenRefreshView -> POST data:", request.data)
        response = super().post(request, *args, **kwargs)
        print("Refresh response data:", response.data)
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    print("Register -> POST data:", request.data)
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        print("Register -> usuario creado:", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("Register -> errores:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    print("Logout -> user:", request.user)
    return Response({"detail": "Logout success"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_todos(request):
    print("get_todos -> user:", request.user)
    todos = Todo.objects.filter(owner=request.user)
    serializer = TodoSerializer(todos, many=True)
    print("get_todos -> response:", serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    print("is_logged_in -> user:", request.user)
    serializer = UserSerializer(request.user)
    print("is_logged_in -> response:", serializer.data)
    return Response(serializer.data)


class VideoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        print("VideoUploadView -> POST data:", request.data)
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            print("VideoUploadView -> serializer válido, asignando user.")
            serializer.save(user=request.user)
            print("VideoUploadView -> video guardado:", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("VideoUploadView -> errores:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comments(request, video_id):
    comments = Comment.objects.filter(
        video_id=video_id).order_by('-created_at')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, video_id):
    text = request.data.get('text')
    if not text:
        return Response({"error": "El comentario no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({"error": "Video no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    comment = Comment(user=request.user, video=video, text=text)
    comment.save()
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_comment(request, comment_id):
    text = request.data.get('text')
    if not text:
        return Response({"error": "El comentario no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
    except Comment.DoesNotExist:
        return Response({"error": "Comentario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    comment.text = text
    comment.save()
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
    except Comment.DoesNotExist:
        return Response({"error": "Comentario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    comment.delete()
    return Response({"detail": "Comentario eliminado"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def popular_videos(request):
    """
    Devuelve los 5 vídeos más populares basados en:
      - Me gusta: +10 puntos cada uno.
      - No me gusta: -5 puntos cada uno.
      - Comentarios: +1 punto cada uno.
      - Bonus temporal: vídeo de hoy +100, de ayer 0, de anteayer -100, etc.
    Se incluyen sólo vídeos del mes en curso. Si no hay, se eligen 5 al azar.
    Si todos los vídeos tienen la misma popularidad, se eligen 5 al azar.
    """
    today = date.today()
    current_month_videos = Video.objects.filter(
        created_at__year=today.year, created_at__month=today.month)

    if not current_month_videos.exists():
        videos = list(Video.objects.all())
    else:
        videos = list(current_month_videos)

    video_popularity = []
    for video in videos:
        likes = Reaction.objects.filter(
            video=video, reaction_type=Reaction.LIKE).count()
        dislikes = Reaction.objects.filter(
            video=video, reaction_type=Reaction.DISLIKE).count()
        comments_count = Comment.objects.filter(video=video).count()
        diff = (today - video.created_at.date()).days
        bonus = 100 - (diff * 100)
        popularity = likes * 10 - dislikes * 5 + comments_count + bonus
        video_popularity.append((video, popularity))

    popularities = [pop for (_, pop) in video_popularity]
    if len(set(popularities)) <= 1:
        selected = random.sample(
            video_popularity, min(5, len(video_popularity)))
    else:
        video_popularity.sort(key=lambda x: x[1], reverse=True)
        selected = video_popularity[:5]

    selected_videos = [video for (video, _) in selected]
    serializer = VideoSerializer(selected_videos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
