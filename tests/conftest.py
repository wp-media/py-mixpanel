import pytest
import typing as t
from unittest.mock import patch, Mock


@pytest.fixture(autouse=True)
def django_settings_mock() -> t.Generator[dict[str, str | None], None, None]:
    settings_dict: dict[str, str | None] = {"TOKEN": "xxx"}
    settings_mock = Mock()
    settings_mock.MIXPANEL_OPTIONS = settings_dict
    with (
        patch(
            "py_mixpanel.DjangoMixpanelMiddleware._get_django_settings",
            return_value=settings_mock,
        ),
        patch(
            "py_mixpanel.DjangoMixpanelMixin._get_django_settings",
            return_value=settings_mock,
        ),
    ):
        yield settings_dict


@pytest.fixture()
def request_mock() -> Mock:
    request_mock = Mock()
    request_mock.path = "/hello-world"
    request_mock.headers = {"User-Agent": "Netscape/1.0"}
    return request_mock
