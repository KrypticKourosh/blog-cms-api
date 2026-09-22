from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Tag, Post
)

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    '''Brief Author representation used in Post related serializers'''
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PostListSerializer(serializers.ModelSerializer):

    # the actual objects (not just the id)
    author = AuthorSerializer(read_only=True) # author is set automatically
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_liked = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_featured_image(self, obj):
        '''Return image URL if it exists'''
        request = self.context.get('request')

        if obj.featured_image and hasattr(obj.featured_image, 'url'):
            relative_url = obj.featured_image.url
            if request is not None:
                return request.build_absolute_uri(relative_url)
            return relative_url
        return None
                
class PostDetailSerializer(serializers.ModelSerializer):
    '''
    Use this serializer to retrieve / create / update
    
    Read-only fields are returned only on /GET/ requests.

    Write-only fields should be mentioned in the body on /POST/ requests.
    '''

    # read-only fields: (for retrieve action)
    author = AuthorSerializer(read_only=True) # author is set automatically
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_liked = serializers.SerializerMethodField()
    featured_image = serializers.ImageField(required=False, allow_null=True) # upload


    # write-only fields for create / update:
    # check if the category_id and the tag_ids exist in the db
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True, # Don't display on /GET/
        required=True, 
        allow_null=False,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        many=True,
        required=False 
    )

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'slug',
            'author',
            'views_count',
            'likes_count',
            'created_at',
            'updated_at',
            'published_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        '''Return absolute URL for images (if a request is sent)'''
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if instance.featured_image and hasattr(instance.featured_image, 'url'):
            relative_url = instance.featured_image.url
            if request is not None:
                abosulte_url = request.build_absolute_uri(relative_url)
                representation['featured_image'] = abosulte_url
            else: # no request / project-level use 
                representation['featured_image'] = relative_url

        return representation
    
    def create(self, validated_data):
        '''
        Since tags has a many-to-many relation with post
        you can't do:
        Post.objects.create(title='...', tags=[1, 2])

        You should set it like:

        post = Post.objects.create(title='...')
        post.tags.set([1, 2])
        '''
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        if tags:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])

        # new image
        if 'featured_image' in validated_data:
            # delete old image if exists
            if instance.featured_image:
                instance.featured_image.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if tags:
            instance.tags.set(tags)
        return instance