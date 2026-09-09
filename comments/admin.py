from django.contrib import admin
from .models import Comment

# admin.site.register(Comment)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'post',
        'author',
        'created_at',
        'parent',
        'is_active'
    ]
    list_filter = [
        'post',
        'author',
        'is_active',
        'created_at',
    ]
    search_fields = [
        'post__title',
        'author__username',
        'content',
    ]
    # uncomment on deploy
    # raw_id_fields = (
    #     'post',
    #     'author',
    #     'parent'
    # )