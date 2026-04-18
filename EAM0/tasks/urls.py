from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ProjectListViewSet, UserListViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"projects", ProjectListViewSet, basename="project-list")
router.register(r"users", UserListViewSet, basename="user-list")

urlpatterns = [
    path("", include(router.urls)),
]