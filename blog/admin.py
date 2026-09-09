from django.contrib import admin
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
        'id',
        'title',
        'author',
        'category',
        'status',
        'created_at',
        'published_at'
    )
    list_filter = ('category', 'status', 'author')
    search_fields = (
        'title',
        'content',
        'author__username',
        'tags__name',
        )
    prepopulated_fields = {'slug': ('title', )}
    
    # raw_id_fields = ("author",) # use for large datasets
    # date_hierarchy = "created_at"
    # filter_horizontal = ("tags",)

