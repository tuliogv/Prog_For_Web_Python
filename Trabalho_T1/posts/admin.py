from django.contrib import admin
from .models import Post, Attachment

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created_at", "updated_at")
    search_fields = ("author__username", "message")
    list_filter = ("created_at",)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "content_type", "original_name", "uploaded_at")
