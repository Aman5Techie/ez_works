from django.db import models

class UploadedFile(models.Model):
    unique_id = models.CharField(max_length=6, unique=True)
    file_url = models.URLField()
    original_file_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.original_file_name
