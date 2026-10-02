from rest_framework.permissions import BasePermission


class IsStaffOrReadOnly(BasePermission):
    """
    Anyone authenticated can read.
    Only staff users can create/update/delete.
    """

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.is_authenticated

        return (
            request.user.is_authenticated
            and request.user.is_staff
        )