class DjangoMixpanelMixin:
    """
    Use this mixin in a class-based view to easily track events
    in Mixpanel.
    """

    def track(self, payload: dict) -> None: ...
