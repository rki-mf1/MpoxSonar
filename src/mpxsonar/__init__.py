import logging

from .config import LOG_LEVEL

# Determine version using pyproject.toml file
try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"


logging.basicConfig(
    format="MPoxSonar:%(asctime)s %(levelname)-4s: %(message)s",
    level=LOG_LEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
)
