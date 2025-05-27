"""Main tracking functionality for Mixpanel."""

import hashlib
from typing import Any, Dict

import mixpanel


class Tracking:
    """Mixpanel tracking wrapper with utility methods."""

    def __init__(self, mixpanel_token: str, feature_flag: bool = True):
        """
        Initialize Mixpanel tracking.

        Args:
            mixpanel_token: Mixpanel project token
        """
        self.mixpanel = mixpanel.Mixpanel(
            mixpanel_token,
            consumer=mixpanel.Consumer(api_host="api-eu.mixpanel.com"),
        )
        self.feature_flag = feature_flag

    def track(self, user_id, event: str, properties: Dict[str, Any]) -> None:
        """
        Track an event in Mixpanel.

        Args:
            event: Event name
            properties: Event properties dictionary
        """
        if not self.feature_flag:
            return
        self.mixpanel.track(self.hash(user_id), event, properties)

    def set_user_property(self, user_id: str, property_name: str, value: Any) -> None:
        """
        Set a user property in Mixpanel.

        Args:
            user_id: User ID
            property_name: Property name
            value: Property value
        """
        if not self.feature_flag:
            return
        self.mixpanel.people_set(
            user_id,
            {property_name: value}
        )

    def hash(self, value: str) -> str:
        """
        Hash a value using SHA3-224.

        Args:
            value: Value to hash

        Returns:
            Hashed string
        """
        if not self.feature_flag:
            return
        return hashlib.sha3_224(value.encode('utf-8')).hexdigest()
