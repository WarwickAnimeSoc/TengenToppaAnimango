import django.db.models as models

class RateLimit(models.Model):
    """
    Automatically ensures unique pairs of scope-identifier-route.

    Route is used to identifier the URL endpoint it is guarding against.

    Max scope length is 20.
    Max identifier length is 128.
    Max route length is 128.

    A background task is expected to auto-clear all expired rate limits,
    to keep database from growing forever without need.
    """

    MAX_SCOPE_LENGTH=20
    MAX_IDENTIFIER_LENGTH=128
    MAX_ROUTE_LENGTH=128

    scope = models.CharField(max_length=MAX_SCOPE_LENGTH)
    identifier = models.CharField(max_length=MAX_IDENTIFIER_LENGTH)
    route = models.CharField(max_length=MAX_ROUTE_LENGTH)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    exceeded = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "identifier", "route"],
                name="unique_rate_limit",
            )
        ]
        indexes = [
            models.Index(fields=["expires_at"])
        ]


