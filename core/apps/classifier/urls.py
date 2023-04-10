from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.imageclassifier, name='image-classifier'),
    path('download_report/', views.download_report, name='download_report'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

