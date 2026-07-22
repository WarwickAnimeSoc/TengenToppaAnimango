"""
Created as a custom rate limiter,
to avoid pulling in third party dependencies.
"""

import django.utils.timezone as timezone
from datetime import timedelta
from django.http import HttpRequest
from django.db import transaction, IntegrityError, DatabaseError

from .models import RateLimit

def reject_window(request: HttpRequest, scope: str, identifier: str, max_request: int, window: timedelta) -> bool:
    """Rejects the request under the provided rate limiting window and identification.

    :param request: Rate limit will apply to this request.
    :param scope: Rate limit will apply under this custom scope.
        See source code for max length limit.
    :param identifier: Rate limit will apply under this identifier unique within the scope.
        See source code for max length limit.
    :param max_request: The maximum number of requests (inclusively) the rate limit window will accept.
    :param window: How long should the rate limit count for.

    :returns: Should the request be rejected? ``True`` for reject, ``False`` for accept.

    :raises ValueError: When provided parameters is not valid.
    """

    # parameter validations for future references

    if request.resolver_match is None:
        raise ValueError('this function is expected to run in normal view endpoints,'
                         'where request.resolver_match is initialised.')

    if len(scope) > RateLimit.MAX_SCOPE_LENGTH:
        raise ValueError(f'given scope {scope} is longer than max accepted length {RateLimit.MAX_SCOPE_LENGTH}.')

    if len(identifier) > RateLimit.MAX_IDENTIFIER_LENGTH:
        raise ValueError(f'given identifier {identifier} is longer than max accepted length {RateLimit.MAX_IDENTIFIER_LENGTH}.')

    route = request.resolver_match.route,
    if len(route) > RateLimit.MAX_ROUTE_LENGTH:
        raise ValueError(f'given route {route} is longer than max accepted length {RateLimit.MAX_ROUTE_LENGTH}.')

    if max_request < 0:
        raise ValueError(f'expected max request to be 0 or more.')

    # try required to deal with race condition of concurrent requests
    # rejects prematurely over race condition as we do not expect it to occur under normal usage
    try:
        with transaction.atomic():
            now = timezone.now()
            limiter, _ = RateLimit.objects.select_for_update().get_or_create(
                scope=scope,
                identifier=identifier,
                route=route,
                defaults={
                    'count': 0,
                    'expires_at': now + window,
                },
            )

            if limiter.expires_at <= now:
                limiter.count = 0
                limiter.expires_at = now + window

            limiter.count += 1
            limiter.save(update_fields=['count', 'expires_at'])

            return limiter.count > max_request

    except (IntegrityError, DatabaseError):
        return True


def reject_ip(request: HttpRequest, max_request: int, window: timedelta) -> bool:
    """Rejects request based on IP address.

    Alias for 
    .. code-block:: python
        reject_window(request, 'ip', get_ip(request), max_request, window)

    See ``reject_window()`` for more documentation.
    """
    return reject_window(request, 'ip', get_ip(request), max_request, window)


def get_ip(request: HttpRequest) -> str:
    """Gets the IP address of the request.
    .. warning::
        Blindly assumes ``X_FORWARDED_FOR`` and ``REMOTE_ADDR`` are assigned by proxy and not client injected.
    """
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        # X-Forwarded-For may contain multiple IPs.
        # First IP is assumed to be the client.
        return forwarded_for.split(",")[0].strip()

    # both production and development deployment will pretty much always set this
    # safe to assume always set
    return request.META.get("REMOTE_ADDR", "unknown")
