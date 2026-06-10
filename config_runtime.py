"""Runtime-safe config loader.

Local development can keep using the ignored ``config.py`` file, while hosted
deployments fall back to the checked-in cloud defaults.
"""

try:
    from config import *  # type: ignore  # noqa: F401,F403
except ModuleNotFoundError as exc:
    if exc.name != "config":
        raise
    from config_cloud import *  # type: ignore  # noqa: F401,F403

