import pytest
import typing as t
from unittest.mock import patch, Mock, MagicMock, ANY

from py_mixpanel import DjangoMiddleware


@pytest.fixture(autouse=True)
def django_settings_mock() -> t.Generator[dict[str, str | None], None, None]:
    settings_dict: dict[str, str | None] = {}
    settings_mock = Mock()
    settings_mock.MIXPANEL_OPTIONS = settings_dict
    with patch(
        "py_mixpanel.DjangoMiddleware._get_django_settings", return_value=settings_mock
    ):
        yield settings_dict


@pytest.fixture()
def tracker_mock() -> t.Generator[MagicMock, None, None]:
    with patch("py_mixpanel.django_middleware.Tracking") as mock:
        yield mock


def test_initialization(django_settings_mock: Mock) -> None:
    get_response = Mock()
    middleware = DjangoMiddleware(get_response)
    assert middleware.get_response == get_response
    assert middleware.settings == django_settings_mock


def test_get_payload() -> None:
    middleware = DjangoMiddleware(Mock())
    request_mock = Mock()
    request_mock.path = "/hello-world"
    payload = middleware.get_payload(request_mock)
    assert payload == {
        "origin": "django-middleware",
        "page": "/hello-world",
    }


def test_get_payload_with_setting_dict(django_settings_mock: dict) -> None:
    django_settings_mock["PAGE_VIEW_EVENT_PAYLOAD"] = {"a": "1", "b": "2"}
    middleware = DjangoMiddleware(Mock())
    request_mock = Mock()
    request_mock.path = "/hello-world"
    payload = middleware.get_payload(request_mock)
    assert payload == {
        "origin": "django-middleware",
        "page": "/hello-world",
        "a": "1",
        "b": "2",
    }


@pytest.mark.parametrize(
    "setting,is_authenticated,does_tracking",
    [
        (None, True, True),
        (False, True, False),
        (False, False, False),
        (True, True, True),
        (True, False, False),
    ],
)
def test_tracking_enabled(
    django_settings_mock: dict,
    tracker_mock: Mock,
    setting: str | None,
    is_authenticated: bool,
    does_tracking: bool,
) -> None:
    if setting is not None:
        django_settings_mock["ENABLE_TRACKING"] = setting

    middleware = DjangoMiddleware(Mock())

    request_mock = Mock()
    request_mock.user.is_authenticated = is_authenticated

    middleware(request_mock)
    assert bool(tracker_mock.call_count) == does_tracking


def test_tracking(
    tracker_mock: Mock,
) -> None:
    middleware = DjangoMiddleware(Mock())

    request_mock = Mock()
    request_mock.user.is_authenticated = True
    request_mock.path = "/hello-world"
    request_mock.user.email = "mark@mark.com"

    tracking_instance = Mock()
    tracker_mock.return_value = tracking_instance

    middleware(request_mock)

    tracker_mock.assert_called_once_with(
        mixpanel_token="",
        enable_tracking=True,
        api_host=None,
    )
    tracking_instance.track.assert_called_once_with(
        "mark@mark.com",
        "Page Viewed",
        {
            "origin": "django-middleware",
            "page": "/hello-world",
        },
    )


def test_tracking_with_custom_event_name(
    django_settings_mock: dict,
    tracker_mock: Mock,
) -> None:
    django_settings_mock["PAGE_VIEW_EVENT_NAME"] = "A Custom Event"

    middleware = DjangoMiddleware(Mock())

    request_mock = Mock()
    request_mock.user.is_authenticated = True

    tracking_instance = Mock()
    tracker_mock.return_value = tracking_instance

    middleware(request_mock)

    tracking_instance.track.assert_called_once_with(
        ANY,
        "A Custom Event",
        ANY,
    )


@pytest.mark.parametrize(
    "setting,in_session,does_user_tracking",
    [
        (None, True, False),
        (False, True, False),
        (False, False, False),
        (True, True, False),
        (True, False, False),
    ],
)
def test_user_tracking_enabled(
    django_settings_mock: dict,
    tracker_mock: Mock,
    setting: str | bool | None,
    in_session: bool,
    does_user_tracking: bool,
) -> None:
    if setting is not None:
        django_settings_mock["USER_TRACKING"] = setting

    middleware = DjangoMiddleware(Mock())

    request_mock = Mock()
    request_mock.user.email = "mark@mark.com"
    request_mock.session = {"_py_mixpanel": True} if in_session else {}

    middleware(request_mock)
    assert bool(tracker_mock.set_user_properties.call_count) == does_user_tracking
    if does_user_tracking:
        assert request_mock.session == {"_py_mixpanel": True}


def test_user_tracking(
    django_settings_mock: dict,
    tracker_mock: Mock,
) -> None:
    django_settings_mock["USER_TRACKING"] = True

    middleware = DjangoMiddleware(Mock())

    request_mock = Mock()
    request_mock.user.email = "mark@domain.com"
    request_mock.session = {}

    tracking_instance = Mock()
    hashing_instance = Mock()
    tracker_mock.return_value = tracking_instance
    tracking_instance.hash = hashing_instance
    hashing_instance.return_value = "abc123"

    middleware(request_mock)

    tracking_instance.set_user_properties.assert_called_once_with(
        "mark@domain.com",
        {
            "email_domain": "abc123",
        },
    )
    hashing_instance.assert_called_once_with("domain.com")


def test_middleware_renders_response() -> None:
    SENTINEL = "f1108656-8667-41fd-92c0-520840ac9579"
    get_response_mock = Mock()
    get_response_mock.return_value = SENTINEL
    middleware = DjangoMiddleware(get_response_mock)
    request_mock = Mock()
    request_mock.user.is_authenticated = False

    response = middleware(request_mock)

    get_response_mock.assert_called_once_with(request_mock)
    assert response == SENTINEL
