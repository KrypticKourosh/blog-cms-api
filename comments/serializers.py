from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class CommentAuthorSerializer(serializers.ModelSerializer):
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
    author = CommentAuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = [
            'is_active', 
            'author',
            'post',
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
        if not parent: 
            return attrs # no parent no reply 

        view = self.context['view']
        post_slug = view.kwargs.get('post_slug')

        from blog.models import Post
        post = get_object_or_404(Post, slug=post_slug)

        if parent.post_id != post.id: # type: ignore
            raise serializers.ValidationError({
                'parent': 'You can only reply to the comments on the same post.'
            })
        return attrs

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']