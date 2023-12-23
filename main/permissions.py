from rest_framework.permissions import BasePermission


class IsActive(BasePermission):
    """
    Custom permission to only allow active users to access services.
    """

    def has_permission(self, request, view):
        return request.user.is_active


class IsSameUserOrStaff(BasePermission):
    """
    Custom permission to only allow the same user or staff users to view details.
    Staff users are also the ones in the admin group.
    """

    def has_object_permission(self, request, view, obj):
        # Don't allow users to delete themselves
        if request.method == "DELETE" and obj == request.user:
            return False

        # Allow staff and admin group users
        if request.user.is_staff or request.user.groups.filter(name="admin").exists():
            return True

        # Don't allow non-staff users to update their staff, is_admin, or is_active fields
        if request.method in ["PUT", "PATCH"]:
            if "is_staff" in request.data:
                return False
            if (
                "is_admin" in request.data
                or "is_active" in request.data
                and not request.user.groups.filter(name="admin").exists()
            ):
                return False

        # Allow if the requested user matches the object
        return obj == request.user


class IsInAdminGroupOrStaff(BasePermission):
    """
    Custom permission to only allow users in the admin group.
    """

    group_name = "admin"

    def has_permission(self, request, view):
        # Allow staff users
        if request.user.is_staff:
            return True

        # Allow if the user is in the admin group
        return request.user.groups.filter(name=self.group_name).exists()
