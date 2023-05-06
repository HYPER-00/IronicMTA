"""
    PyMTA Logger
"""

import logging
import colorama
import os
from settings_manager import SettingsManager

class Logger:
    """
        Logger class\n
        use it instead of 'print()'
    """
    def __init__(self) -> None:
        colorama.init(autoreset=True)

        self.settings = SettingsManager()
        self.settings = self.settings.get()

        self._localdir = __file__.split('\\')[:-1]
        if self._localdir[0].endswith(':'): self._localdir[0] += '\\'
        self._localdir = os.path.join(*self._localdir)
        _logs_folder = os.path.join(self._localdir, "logs")
        if not os.path.isdir(_logs_folder):
            os.mkdir(_logs_folder)

        logging.basicConfig(
            filename=self.settings['logfile'], filemode='a', format='[%(asctime)s] %(levelname)s : %(message)s')
        self.logger = logging.getLogger()

        self.warn_format = logging.Formatter(
            fmt=colorama.Fore.YELLOW + '[%(asctime)s][%(levelname)s]:  %(message)s')
        self.error_format = logging.Formatter(
            fmt=colorama.Fore.RED + '[%(asctime)s][%(levelname)s]:  %(message)s')
        self.success_format = logging.Formatter(
            fmt=colorama.Fore.GREEN + '[%(asctime)s][%(levelname)s]:  %(message)s')
        self.log_format = logging.Formatter(
            fmt=colorama.Fore.LIGHTBLACK_EX + '[%(asctime)s][%(levelname)s]: ' + colorama.Fore.RESET + ' %(message)s')

        self.logger.setLevel(logging.DEBUG)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(self.log_format)

        self.logger.addHandler(self.console_handler)

    def log(self, message: str) -> None:
        """
            Log Text
            Color: White
        """
        self.console_handler.setFormatter(self.log_format)
        return self.logger.info(msg=message.strip())

    def warn(self, message: str) -> None:
        """
            Warn Log
            Color: Yellow
        """
        self.console_handler.setFormatter(self.warn_format)
        return self.logger.warning(msg=message.strip())

    def error(self, message: str) -> None:
        """
            Error Log
            Color: Red
        """
        self.console_handler.setFormatter(self.error_format)
        return self.logger.error(msg=message.strip())

    def success(self, message: str) -> None:
        """
            Sucess Log
            Color: Green
        """
        self.console_handler.setFormatter(self.success_format)
        return self.logger.info(msg=message.strip())
