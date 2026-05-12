from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsTravelOwnerOrPublicReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        travel = getattr(obj, 'travel', obj)
        owner = travel.cat.owner
        if request.method in SAFE_METHODS:
            return travel.is_public or owner == request.user
        return owner == request.user


class IsTravelOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        travel = getattr(obj, 'travel', obj)
        return travel.cat.owner == request.user
