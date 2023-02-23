from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('image-classifier/', views.imageclassifier, name='image-classifier')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
