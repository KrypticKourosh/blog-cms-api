from rest_framework import permissions

class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the author of the comment or a staff can edit the comment
        return request.user == obj.author or request.user.is_staff