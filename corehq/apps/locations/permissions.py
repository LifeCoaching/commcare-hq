from django_prbac.decorators import requires_privilege_raise404
from corehq import privileges
from functools import wraps
from django.http import Http404
from .models import SQLLocation
from corehq.apps.domain.decorators import (login_and_domain_required,
                                           domain_admin_required)


def locations_access_required(view_fn):
    """
    Decorator controlling domain-level access to locations.
    """
    return login_and_domain_required(
        requires_privilege_raise404(privileges.LOCATIONS)(view_fn)
    )


def is_locations_admin(view_fn):
    """
    Decorator controlling write access to locations.
    """
    return locations_access_required(domain_admin_required(view_fn))


def user_can_edit_location(user, sql_location, project):
    if (user.is_domain_admin(project.name) or
            not project.location_restriction_for_users):
        return True

    user_loc = user.get_location(sql_location.domain)
    if user_loc:
        user_loc = user_loc.sql_location
    return user_loc is None or user_loc.is_direct_ancestor_of(sql_location)


def user_can_view_location(user, sql_location, project):
    if (user.is_domain_admin(project.name) or
            not project.location_restriction_for_users):
        return True

    user_loc = user.get_location(sql_location.domain)
    if not user_loc:
        return True

    if user_can_edit_location(user, sql_location, project):
        return True

    return sql_location.location_id in user_loc.lineage


def can_edit_location(view_fn):
    """
    Decorator controlling a user's access to a specific location.
    The decorated function must be passed a loc_id arg (eg: from urls.py)
    """
    @wraps(view_fn)
    def _inner(request, domain, loc_id, *args, **kwargs):
        try:
            # pass to view?
            location = SQLLocation.objects.get(location_id=loc_id)
        except SQLLocation.DoesNotExist:
            raise Http404()
        else:
            if user_can_edit_location(request.couch_user, location, request.project):
                return view_fn(request, domain, loc_id, *args, **kwargs)
        raise Http404()
    return locations_access_required(_inner)


def user_can_edit_location_types(user, project):
    if (user.is_domain_admin(project.name) or
            not project.location_restriction_for_users):
        return True

    return not user.get_domain_membership(project.name).location_id


def can_edit_location_types(view_fn):
    """
    Decorator controlling a user's access to a location types.
    """
    @wraps(view_fn)
    def _inner(request, domain, *args, **kwargs):
        if user_can_edit_location_types(request.couch_user, request.project):
            return view_fn(request, domain, *args, **kwargs)
        raise Http404()
    return locations_access_required(_inner)
