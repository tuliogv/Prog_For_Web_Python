from django.db import models
from django.contrib.auth.models import User
import mimetypes

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.message[:30]}"

def attachment_upload_to(instance, filename):
    # salva separado por ano/mes/dia
    return f"attachments/{instance.post_id or 'tmp'}/{filename}"

class Attachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=attachment_upload_to)
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if self.file and not self.content_type:
            guess, _ = mimetypes.guess_type(self.file.name)
            self.content_type = guess or ""
        if self.file and not self.original_name:
            self.original_name = getattr(self.file, "name", "") or self.original_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_name or self.file.name