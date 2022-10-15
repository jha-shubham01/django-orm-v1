from rest_framework import viewsets

from .models import Category, Comment, Like, Post
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    LikeSerializer,
    PostSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikeViewSet(viewsets.ModelViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class PostViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
