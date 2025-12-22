from unittest.mock import patch, Mock

from py_mixpanel import Tracking


@patch("mixpanel.Mixpanel")
@patch("mixpanel.Consumer")
def test_initialization(consumer_mock: Mock, mixpanel_mock: Mock) -> None:
    consumer_instance = Mock()
    mixpanel_instance = Mock()
    consumer_mock.return_value = consumer_instance
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", enable_tracking=False)

    consumer_mock.assert_called_once_with(api_host="api-eu.mixpanel.com")
    mixpanel_mock.assert_called_once_with(
        "abc",
        consumer=consumer_instance,
    )
    assert tracker.mixpanel == mixpanel_instance
    assert not tracker.enable_tracking


@patch("mixpanel.Consumer")
def test_different_api_host(consumer_mock: Mock) -> None:
    Tracking("abc", api_host="my-custom-host.local")
    consumer_mock.assert_called_once_with(api_host="my-custom-host.local")


@patch("py_mixpanel.tracking.hashlib.sha224")
@patch("mixpanel.Mixpanel")
def test_enable_tracking_true(mixpanel_mock: Mock, hashlib_mock: Mock) -> None:
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", enable_tracking=True)
    tracker.track("abc", "def", {})
    tracker.set_user_property("abc", "def", "xyz")
    tracker.hash("xxx")

    assert mixpanel_instance.track.call_count == 1
    assert mixpanel_instance.people_set.call_count == 1
    assert hashlib_mock.call_count > 1


@patch("mixpanel.Mixpanel")
def test_enable_tracking_false(mixpanel_mock: Mock) -> None:
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", enable_tracking=False)
    tracker.track("abc", "def", {})
    tracker.set_user_property("abc", "def", "xyz")

    assert mixpanel_instance.track.call_count == 0
    assert mixpanel_instance.people_set.call_count == 0


@patch("py_mixpanel.tracking.hashlib.sha224")
@patch("mixpanel.Mixpanel")
def test_deprecated_feature_flag_parameter_enable_tracking(
    mixpanel_mock: Mock, hashlib_mock: Mock
) -> None:
    # @feature-flag-param-deprecated
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", feature_flag=True)
    tracker.track("abc", "def", {})
    tracker.set_user_property("abc", "def", "xyz")
    tracker.hash("xxx")

    assert mixpanel_instance.track.call_count == 1
    assert mixpanel_instance.people_set.call_count == 1
    assert hashlib_mock.call_count > 1


@patch("mixpanel.Mixpanel")
def test_deprecated_feature_flag_parameter_disabled(mixpanel_mock: Mock) -> None:
    # @feature-flag-param-deprecated
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", feature_flag=False)
    tracker.track("abc", "def", {})
    tracker.set_user_property("abc", "def", "xyz")

    assert mixpanel_instance.track.call_count == 0
    assert mixpanel_instance.people_set.call_count == 0


@patch("mixpanel.Mixpanel")
def test_tracking(mixpanel_mock: Mock) -> None:
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", enable_tracking=True)
    tracker.track("mark", "some_event", {"a": 1})

    mixpanel_instance.track.assert_called_once_with(
        "b9e09e7675f9103783963b8cafa4992c7430ff1e21dd490ef8972cff",
        "some_event",
        {"a": 1},
    )


@patch("mixpanel.Mixpanel")
def test_set_user_property(mixpanel_mock: Mock) -> None:
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", enable_tracking=True)
    tracker.set_user_property("mark", "some_property", "some_value")

    mixpanel_instance.people_set.assert_called_once_with(
        "b9e09e7675f9103783963b8cafa4992c7430ff1e21dd490ef8972cff",
        {"some_property": "some_value"},
    )


@patch("mixpanel.Mixpanel")
def test_hashing(mixpanel_mock: Mock) -> None:
    mixpanel_instance = Mock()
    mixpanel_mock.return_value = mixpanel_instance

    tracker = Tracking("abc", enable_tracking=True)

    assert (
        tracker.hash("Hey there! ✨")
        == "cbb191a99676855af0093cb88834e86d61f941a4964ebabd357c77c0"
    )
