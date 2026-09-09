from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission that only allows the owner of an object
    (via a `student_profile.user` or `user` attribute) or staff/admin
    users to view/edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or getattr(request.user, 'role', None) == 'admin':
            return True

        owner = getattr(obj, 'user', None)
        if owner is None:
            profile = getattr(obj, 'student_profile', None)
            owner = getattr(profile, 'user', None)
        return owner == request.user


class IsCounselorOrAdmin(permissions.BasePermission):
    """Allows access only to counselors or admin users (for managing catalog data)."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, 'role', None) in ('counselor', 'admin'))
        )
