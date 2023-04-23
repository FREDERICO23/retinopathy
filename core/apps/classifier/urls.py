from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('classifier/', views.imageclassifier, name='image-classifier'),
    path('register/',views.register, name="register"),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name="logout"),  
    path('generate_report/', views.generate_report, name='generate_report'),
    path('download_report/', views.download_report, name='download_report'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

