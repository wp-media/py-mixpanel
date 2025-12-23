import typing as t

from .tracking import Tracking, ANONYMOUS_USER_ID

if t.TYPE_CHECKING:
    from django.conf import LazySettings
    from django.http import HttpRequest


class DjangoMixpanelMixin:
    """
    Use this mixin in a class-based view to easily track events
    in Mixpanel.
    """

    def _get_django_settings(self) -> LazySettings:
        from django.conf import settings

        return settings

    def mixpanel_get_payload(
        self, request: HttpRequest, payload: dict[str, t.Any]
    ) -> dict[str, t.Any]:
        base = {
            "origin": "django-view-mixin",
            "page": request.path,
        }
        base.update(payload)
        return base

    def mixpanel_track(self, event: str, payload: dict[str, t.Any]) -> None:
        settings = getattr(self._get_django_settings(), "MIXPANEL_OPTIONS", {})

        if not (
            bool(settings.get("ENABLE_TRACKING", True))
            and settings.get("TOKEN", "")
            and hasattr(self, "request")
        ):
            return

        user_id = (
            self.request.user.email
            if self.request.is_authenticated and hasattr(self.request.user, "email")
            else ANONYMOUS_USER_ID
        )
        tracker = Tracking(
            mixpanel_token=settings.get("TOKEN", ""),
            enable_tracking=True,
            api_host=settings.get("API_HOST"),
        )
        tracker.track(user_id, event, self.mixpanel_get_payload(self.request, payload))
