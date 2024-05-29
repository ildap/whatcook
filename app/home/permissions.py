from django.contrib.auth.models import User
from django.db import transaction

from rest_framework.permissions import DjangoObjectPermissions

from guardian.shortcuts import assign_perm


class DjangoObjectPermissionsOrAnonReadOnly(DjangoObjectPermissions):
    authenticated_users_only = False


class PermissionsMixin:
    permission_classes = [DjangoObjectPermissionsOrAnonReadOnly]

    @transaction.atomic
    def perform_create(self, serializer):
        obj = serializer.save()
        self._assign_object_perms(obj)

    def _assign_object_perms(self, object):
        user = self.request.user
        name = object.__class__.__name__.lower()
        assign_perm('home.change_' + name, user, object)
        assign_perm('home.delete_' + name, user, object)