# comptes/permissions.py
from rest_framework import permissions

class IsPassager(permissions.BasePermission):
    """
    Allows access only to users with role == 'passager'.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "passager")

class IsChauffeur(permissions.BasePermission):
    """
    Allows access only to users with role == 'chauffeur'.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "chauffeur")

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to Django superusers (admin via /admin/).
    Useful for internal endpoints that only superadmins should call.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)
