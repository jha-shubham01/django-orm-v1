from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("category", views.CategoryViewSet, basename="category")
router.register("comments", views.CommentViewSet, basename="comments")
router.register("likes", views.LikeViewSet, basename="likes")
router.register("posts", views.PostViewSet, basename="posts")

urlpatterns = router.urls
