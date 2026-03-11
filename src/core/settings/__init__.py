import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    from .production import *  # noqa: F401, F403
elif ENVIRONMENT == "staging":
    from .staging import *  # noqa: F401, F403
else:
    from .development import *  # noqa: F401, F403
