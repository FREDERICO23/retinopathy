from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    prediction = models.CharField(max_length=255, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)