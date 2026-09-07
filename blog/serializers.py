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

    class Meta:
        model = Post
        fields = '__all__'

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
            'updated_at'
        ]

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
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags:
            instance.tags.set(tags)
        return instance
        