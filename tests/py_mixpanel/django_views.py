import pytest
import typing as t
from unittest.mock import patch, Mock, MagicMock

from py_mixpanel import DjangoMixpanelMixin


@pytest.fixture()
def tracker_mock() -> t.Generator[MagicMock, None, None]:
    with patch("py_mixpanel.django_views.Tracking") as mock:
        yield mock


def test_get_payload(request_mock: Mock) -> None:
    instance = DjangoMixpanelMixin()
    request_mock.get_host = lambda: "example.com"
    result = instance.mixpanel_get_payload(request_mock, {"a": 1})
    assert result == {
        "a": 1,
        "origin": "django-view-mixin",
        "page": "/hello-world",
        "host": "example.com",
    }


def test_get_payload_empty(request_mock: Mock) -> None:
    instance = DjangoMixpanelMixin()
    request_mock.get_host = lambda: "example.com"
    result = instance.mixpanel_get_payload(request_mock, {})
    assert result == {
        "origin": "django-view-mixin",
        "page": "/hello-world",
        "host": "example.com",
    }


@pytest.mark.parametrize(
    "setting_enabled,has_request,is_tracking",
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (None, True, True),
        (False, False, False),
    ],
)
def test_track_enabled(
    django_settings_mock: dict,
    tracker_mock: Mock,
    request_mock: Mock,
    setting_enabled: bool | None,
    has_request: bool,
    is_tracking: bool,
) -> None:
    instance = DjangoMixpanelMixin()

    if setting_enabled is not None:
        django_settings_mock["ENABLE_TRACKING"] = setting_enabled
    else:
        assert "ENABLE_TRACKING" not in django_settings_mock

    if has_request:
        request_mock.user.email = "hey@there.com"
        setattr(instance, "request", request_mock)

    instance.mixpanel_track("X", {})

    assert bool(tracker_mock.call_count) == is_tracking
