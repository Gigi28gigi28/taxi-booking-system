from rest_framework.permissions import BasePermission

class IsAuthenticatedMicroservice(BasePermission):
    
    def has_permission(self, request, view):
        return True
