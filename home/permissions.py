from rest_framework.permissions import DjangoObjectPermissions

from guardian.shortcuts import assign_perm


class DjangoObjectPermissionsOrAnonReadOnly(DjangoObjectPermissions):
    authenticated_users_only = False


def assign_object_perms(user, object):
    name = object.__class__.__name__.lower()
    assign_perm('home.change_' + name, user, object)
    assign_perm('home.delete_' + name, user, object)
