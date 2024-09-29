
from django.urls import path, include
from .views import FileUploadViewSet
from .views import FileDownloadViewSet
from .views import FileDecryptViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'upload', FileUploadViewSet, basename='file-upload')


urlpatterns = [
    path('', include(router.urls)),
    path('download/', FileDownloadViewSet.as_view(),name="download"),
    path('download_file/<str:url>/', FileDecryptViewSet.as_view(),name="download_file"),
]