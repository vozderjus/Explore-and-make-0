from rest_framework import permissions
from .models import Task

class TaskPermission(permissions.BasePermission):
    ALLOWED_FIELDS_BY_ROLE: dict = {
        'author': {'description'},
        'performer': {'status', 'priority'}
    }
    
    def has_object_permission(self, request, view, obj: Task) -> bool:
        user = request.user
        project = obj.project
        
        if project.owner == user:
            return True
        
        if not project.is_member(user):
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.method == 'DELETE':
            return obj.author == user
        
        if request.method in ('PUT', 'PATCH'):
            requested_fields = set(request.data.keys())
            readonly_fields = {'id', 'author', 'created_at', 'updated_at'}
            writable_requested = requested_fields - readonly_fields

            if obj.author == user:
                allowed = self.ALLOWED_FIELDS_BY_ROLE['author']
                return writable_requested.issubset(allowed)

            if obj.performer == user:
                allowed = self.ALLOWED_FIELDS_BY_ROLE['performer']
                return writable_requested.issubset(allowed)

            return False

        return False
        