"""
Custom permissions.
Admin = superuser

"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class AdminCanGetAuthCanPost(BasePermission):
    """
    Custom permission rules for:
    1) Anyone can perform SAFE_METHODS ('GET', 'HEAD', 'OPTIONS')
    2) Admin and submitter have full permissions

    """

    def has_permission(self, request, view):
        """
        :return(Boolean):
        Whether the permission is granted.

        """
        if request.method == 'POST':
            return request.user.is_authenticated
        else:
            return request.user.is_superuser


class IsAdminOrReadOnly(BasePermission):
    """

    """
    def has_permission(self, request, view):
        """
        :return(Boolean):
        Whether the permission is granted.

        """
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_superuser


class IsAdminOrIsClinicOwner(BasePermission):
    """
    Customized permission class to allow admin or clinic owner to
    do put/post on ClinicProfile.
    """
    def has_permission(self, request, view):
        """
        :return(Boolean): Whether the permission is granted.
        """
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_superuser or (request.user.is_authenticated and str(request.user.clinic_uuid) == view.kwargs["uuid"])
