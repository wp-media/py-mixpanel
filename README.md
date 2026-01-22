# Python integration for Mixpanel

This repository provides a comprehensive layer on top of the
[official Python library from Mixpanel](https://pypi.org/project/mixpanel/)
which adds:

* Support for anonymizing email addresses and including them in tracked events
* Django middleware & view support (including support for HTMX)
* Unit tested & providing type hints

## Usage

You can install the package, and then start tracking straight away:

```py
from py_mixpanel import Tracking

tracker = Tracking(mixpanel_token="s3cret")

tracker.track("user@email.com", "Login", {"browser": "Chrome"})
```

### Django

If you use Django, you may also:

* Use the `DjangoMixpanelMiddleware` class to automatically track requests
* Use the `DjangoMixpanelMixin` to add a user-friendly `mixpanel_track()` method to any class-based view

These integrations are configured through your own `settings.py`:

```py
MIXPANEL_OPTIONS = {

    # Your Mixpanel token
    TOKEN: str,

    # Potentially override the API host
    API_HOST: str,

    # Enable or disable actual tracking
    ENABLE_TRACKING: bool,  # default: True

    # Track certain properties for every user using the middleware
    # (uses the session)
    USER_TRACKING: bool,  # default: False

    # Keep track of HTMX headers in fired events
    TRACK_HTMX: bool,  # default: True

    # Name the event that will be sent on every page view
    PAGE_VIEW_EVENT_NAME: str,  # default: "Page Viewed"

    # Provide a static default payload for all events
    PAGE_VIEW_EVENT_PAYLOAD: dict,  # default: {}

    # Paths matching any pattern will not trigger automatic page view events
    EXCLUDE_PATHS: list[str],  # default: []
    # Example: [r"^/api/", r"^/health"] to exclude API and health check endpoints

}
```

## Development

It is recommended to use `uv` to develop locally.

### Testing (pytest)

Run the tests:

```bash
$ uv run pytest
```

### Type checking (mypy)

Run the type checker:

```bash
uv run mypy .
```

### Formatting and linting (ruff)

Run the formatter:

```bash
uv tool run ruff format
```

Run the linter:

```bash
uv tool run ruff check --fix
```
