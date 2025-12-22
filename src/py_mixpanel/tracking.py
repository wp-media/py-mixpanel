import hashlib
import typing as t

import mixpanel


class Tracking:
    def __init__(
        self,
        mixpanel_token: str,
        feature_flag: bool = True,  # deprecated @feature-flag-param-deprecated
        enable_tracking: bool = True,
        api_host: str = "api-eu.mixpanel.com",
    ):
        """
        Initialize an instance of the Mixpanel tracking class.

        Provide a valid `mixpanel_token`. Control the Mixpanel API
        host that is being used using `api_host`.

        Tracking is enabled by default, but can be disabled by passing
        `enable_tracking=False`.

        The `feature_flag` parameter is DEPRECATED and will be removed
        in a future version. @feature-flag-param-deprecated
        """
        self.mixpanel = mixpanel.Mixpanel(
            mixpanel_token,
            consumer=mixpanel.Consumer(api_host=api_host),
        )
        self.enable_tracking = feature_flag and enable_tracking

    def track(self, user_id, event: str, properties: t.Dict[str, t.Any]) -> None:
        """
        Track an event in Mixpanel. Anonymize the user ID.
        """
        if not self.enable_tracking:
            return
        self.mixpanel.track(self.hash(user_id), event, properties)

    def set_user_property(self, user_id: str, property_name: str, value: t.Any) -> None:
        """
        Set a user property in Mixpanel. Anonymize the user ID.
        """
        if not self.enable_tracking:
            return
        self.mixpanel.people_set(self.hash(user_id), {property_name: value})

    def hash(self, user_id: str) -> str:
        """
        Hash the input using SHA-224.

        This has the potential to obscure any personal information by making
        it more difficult to access. E-mail addresses, for example, will
        become impossible to revert unless you have a list of known email
        addresses at your disposal.
        """
        return hashlib.sha224(user_id.encode("utf-8")).hexdigest()
