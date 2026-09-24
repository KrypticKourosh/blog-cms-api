from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from .validators import validate_image_extension, validate_image_size

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True) # can be generated
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs): # generate a slug if empty
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    class Status(models.TextChoices): 
        DRAFT = 'draft', 'Draft' # database value, display value
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    content = models.TextField()
    summary = models.TextField(blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts', # enables user.posts.all()   
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
    )
    status = models.CharField(
        choices=Status.choices,
        max_length=10,
        default=Status.DRAFT
    )

    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    featured_image = models.ImageField(
        upload_to='posts/%Y/%m/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_extension]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-slug']), # for URL searches
            models.Index(fields=['-title']),
            models.Index(fields=['-status']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        '''
        1. Fill the `slug` field (if left empty) by slugifying the title.
        
        since the title is not unique, add a number at the end of the slug for duplicate titles, ex.
            title: "John Doe" ~ slug: "john-doe"
            title: "John Doe" (again) ~ slug: "john-doe-1"

        2. Set published_at according to status
        '''
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            self.slug = slug

        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        if self.status == self.Status.DRAFT:
            self.published_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes' # user.likes.all()
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes' # post.likes.all()
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post') # user can't like a post twice
        ordering = ['-created_at'] # what is the defualt?

    def __str__(self):
        return f'{self.user.username} Liked "{self.post.title}"'