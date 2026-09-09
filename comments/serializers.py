from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = [
            'is_active', 
            'author',
            'created_at',
            'updated_at',
        ]

    def get_replies(self, obj):
        if obj.replies.exists():
            active_replies = obj.replies.filter(is_active=True)
            return CommentSerializer(active_replies, many=True).data
        return []

    def validate(self, attrs):
        '''Prevent replying to a comment from a different post'''
        parent = attrs.get('parent')
        post = attrs.get('post')

        if parent:
            if parent.post_id != post.id:
                raise serializers.ValidationError({
                    'parent': 'You can only reply to the comments on the same post.'
                })
        return attrs

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']