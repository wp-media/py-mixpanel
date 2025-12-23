from __future__ import annotations

import typing as t

from .tracking import Tracking, ANONYMOUS_USER_ID

if t.TYPE_CHECKING:
    from django.conf import LazySettings
    from django.http import HttpRequest


MIXPANEL_SESSION_KEY = "_py_mixpanel"
DEFAULT_PAGE_VIEW_EVENT_NAME = "Page Viewed"


class DjangoMixpanelMiddleware:
    """
    A middleware for use with Django that automatically tracks Mixpanel events
    for any request by a logged-in user. Django must be installed in your
    project for this class to be used.
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self.settings: dict = getattr(
            self._get_django_settings(), "MIXPANEL_OPTIONS", {}
        )

    def _get_django_settings(self) -> LazySettings:
        from django.conf import settings

        return settings

    def get_payload(self, request: HttpRequest) -> dict[str, t.Any]:
        """Based on a request, return the desired payload"""

        payload = {
            "origin": "django-middleware",
            "page": str(request.path),
        }

        if self.settings.get("TRACK_HTMX", True):
            payload.update(
                {
                    key.lower(): value
                    for key, value in request.headers.items()
                    if key.upper().startswith("HX-")
                }
            )

        payload.update(self.settings.get("PAGE_VIEW_EVENT_PAYLOAD", {}))
        return payload

    def __call__(self, request: HttpRequest):
        if (
            bool(self.settings.get("ENABLE_TRACKING", True))
            and self.settings.get("TOKEN", "")
            and request.user.is_authenticated
        ):
            user_id = (
                request.user.email
                if hasattr(request.user, "email")
                else ANONYMOUS_USER_ID
            )
            tracker = Tracking(
                mixpanel_token=self.settings.get("TOKEN", ""),
                enable_tracking=True,
                api_host=self.settings.get("API_HOST"),
            )

            if (
                bool(self.settings.get("USER_TRACKING", False))
                and MIXPANEL_SESSION_KEY not in request.session
            ):
                tracker.set_user_properties(
                    user_id, {"email_domain": tracker.hash(user_id.split("@")[-1])}
                )
                request.session[MIXPANEL_SESSION_KEY] = True

            tracker.track(
                user_id,
                self.settings.get("PAGE_VIEW_EVENT_NAME", DEFAULT_PAGE_VIEW_EVENT_NAME),
                self.get_payload(request),
            )

        response = self.get_response(request)
        return response
