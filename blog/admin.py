from django.contrib import admin
from django.utils import timezone
from .models import (
    Category, Tag, Post
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name', )} # as you type, the slug field gets filled
    search_fields = ('name', )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'author', 'category',
        'status', 'created_at', 'published_at'
    )
    list_filter = ('category', 'status', 'author')
    search_fields = (
        'title', 'content', 'author__username',
        'tags__name',
    )
    prepopulated_fields = {'slug': ('title', )}
    
    # raw_id_fields = ("author",) # use for large datasets
    # date_hierarchy = "created_at"
    # filter_horizontal = ("tags",)

    def save_model(self, request, obj, form, change):
        '''Keep status and published_at in sync.'''

        # 1. Set the status but forgot to set the published_at  
        if obj.status == Post.Status.PUBLISHED and obj.published_at is None:
            obj.published_at = timezone.now()

        # 2. Set the published_at but forgot to set the status 
        if obj.published_at is not None and obj.status == Post.Status.DRAFT:
            obj.status = Post.Status.DRAFT

        super().save_model(request, obj, form, change)