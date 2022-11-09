from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import STATUS, Category, Comment, Like, Post
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    LikeSerializer,
    PostSerializer,
    PostValuesSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=["POST"])
    def create_data(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data or None)
        data.is_valid(raise_exception=True)

        title = data.validated_data.get("title")
        slug = data.validated_data.get("slug")
        description = data.validated_data.get("description")

        obj = Category.objects.create(
            title=title, slug=slug, description=description
        )
        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def save_data(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data or None)
        data.is_valid(raise_exception=True)

        title = data.validated_data.get("title")
        slug = data.validated_data.get("slug")
        description = data.validated_data.get("description")

        obj = Category()
        obj.title = title
        obj.slug = slug
        obj.description = description
        obj.save()

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def get_or_create_data(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data or None)
        data.is_valid(raise_exception=True)

        title = data.validated_data.get("title")
        slug = data.validated_data.get("slug")

        obj, _ = Category.objects.get_or_create(title=title, slug=slug)

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def bulk_create(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data or None, many=True)
        data.is_valid(raise_exception=True)

        # Inefficient
        # for row in data.validated_data:
        #     Category.objects.create(
        #       title=row["title"], slug=row["slug"], description=row["description"]
        # )

        # Efficient
        new_data = []
        for row in data.validated_data:
            new_data.append(
                Category(
                    title=row["title"],
                    slug=row["slug"],
                    description=row["description"],
                )
            )

        if new_data:
            new_data = Category.objects.bulk_create(new_data)

        return Response(
            "Successfully created data.", status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @action(detail=False, methods=["GET"])
    def deep_filter_data(self, request, *args, **kwargs):
        # queryset = Comment.objects.all().filter(post__id=1)
        queryset = Comment.objects.all().filter(post__category__id__in=[1, 2])
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class PostViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=["PATCH"])
    def add_category(self, request, pk, *args, **kwargs):

        categories = request.data.get("ids")
        # instance = self.get_object()
        instance = Post.objects.filter(pk=pk).first()

        # Inefficient
        # for category in categories:
        #     instance.category.add(category)

        # Efficient
        categories = set(categories)
        instance.category.add(*categories)

        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"])
    def set_category(self, request, pk, *args, **kwargs):

        categories = request.data.get("ids")
        # instance = self.get_object()
        instance = Post.objects.filter(pk=pk).first()

        # Inefficient
        # instance.category.clear()
        # categories = set(categories)
        # instance.category.add(*categories)

        # Efficient
        instance.category.set(categories)

        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def update_data(self, request, pk, *args, **kwargs):
        summary = request.data.get("summary")
        content = request.data.get("content")
        Post.objects.filter(pk=pk).update(summary=summary, content=content)

        return Response({"message": "Successfully updated the data."})

    @action(detail=False, methods=["POST"])
    def update_or_create_data(self, request, *args, **kwargs):
        category = set(request.data.get("category"))
        content = request.data.get("content")
        summary = request.data.get("summary")
        author = 1
        title = request.data.get("title")

        obj, created = Post.objects.update_or_create(
            title=title,
            defaults={
                "summary": summary,
                "content": content,
                "author_id": author,
            },
        )
        obj.category.set(category)
        print(f"{created=}")

        return Response({"message": "Successfully updated the data."})

    @action(detail=False, methods=["POST"])
    def bulk_update_data(self, request, *args, **kwargs):
        ids = request.data.get("ids")

        queryset = Post.objects.filter(id__in=ids)

        for obj in queryset:
            obj.status = STATUS.PUBLISH.value

        queryset = Post.objects.bulk_update(queryset, ["status"])

        return Response({"message": "Successfully updated the data."})

    @action(detail=False, methods=["GET"])
    def get_all(self, request, *args, **kwargs):

        queryset = Post.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_one(self, request, *args, **kwargs):
        slug = request.GET.get("slug")

        # obj = Post.objects.get(slug=slug)
        # obj = Post.objects.filter(slug=slug).first()

        try:
            obj = Post.objects.get(slug=slug)
        except Post.MultipleObjectsReturned:
            return Response(
                {"message": "Multiple Objects found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Post.DoesNotExist:
            return Response(
                {"message": "Object not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_filter(self, request, *args, **kwargs):
        id = request.GET.get("id")
        queryset = Post.objects.filter(id=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def exclude_filter(self, request, *args, **kwargs):
        id = request.GET.get("id")
        queryset = Post.objects.exclude(id=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def limit_data(self, request, *args, **kwargs):
        # queryset = Post.objects.all()[:1]
        # queryset = Post.objects.all()[1:]
        queryset = Post.objects.all()[1:2]
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def lookup_filter(self, request, *args, **kwargs):
        ids = request.GET.get("ids")
        ids = ids.split(",")
        queryset = Post.objects.filter(id__in=ids)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def order_by_data(self, request, *args, **kwargs):
        queryset = Post.objects.all().order_by("title")
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def distinct_data(self, request, *args, **kwargs):
        queryset = (
            Post.objects.all().filter(category__id__in=[1, 2]).distinct()
        )
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def deep_filter_data(self, request, *args, **kwargs):
        queryset = Post.objects.all().filter(category__id__in=[1, 2])
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["GET"])
    # def reverse_data(self, request, *args, **kwargs):
    #     queryset = Post.objects.filter().reverse()
    #     serializer = self.serializer_class(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def get_values(self, request, pk, *args, **kwargs):
        queryset0 = Post.objects.filter(pk=pk)
        print(queryset0)
        queryset = Post.objects.filter(pk=pk).values("id", "title", "slug")
        # queryset = Post.objects.filter(author=pk).values("id", "title", "slug")
        print(queryset)
        serializer = PostValuesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def get_values_list(self, request, pk, *args, **kwargs):
        queryset0 = Post.objects.filter(pk=pk)
        print(queryset0)
        queryset = Post.objects.filter(pk=pk).values_list(
            "id", "title", "slug"
        )
        # queryset = Post.objects.filter(author=pk).values_list("id", "title", "slug")
        # queryset = Post.objects.filter(author=pk).values_list("title", flat=True)
        print(queryset)
        return Response(queryset, status=status.HTTP_200_OK)
