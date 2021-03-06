"""
Logging utility methods and classes
"""

import logging
from pathlib import Path
import os

from mixer.os_utils import getuser

logger = logging.getLogger(__name__)
logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
        """
        s = super().format(record)
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f" [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


def get_logs_directory():
    def _get_logs_directory():
        import tempfile

        if "MIXER_USER_LOGS_DIR" in os.environ:
            username = getuser()
            base_shared_path = Path(os.environ["MIXER_USER_LOGS_DIR"])
            if os.path.exists(base_shared_path):
                return os.path.join(os.fspath(base_shared_path), username)
            logger.error(
                f"MIXER_USER_LOGS_DIR env var set to {base_shared_path}, but directory does not exists. Falling back to default location."
            )
        return os.path.join(os.fspath(tempfile.gettempdir()), "mixer")

    dir = _get_logs_directory()
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def get_log_file():
    from mixer.share_data import share_data

    return os.path.join(get_logs_directory(), f"mixer_logs_{share_data.run_id}.log")
