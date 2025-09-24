from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created_at", "updated_at")
    search_fields = ("author__username", "message")
    list_filter = ("created_at",)
