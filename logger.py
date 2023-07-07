"""
    SafeServer Logger
"""

import logging
import colorama
import os

class Logger:
    """
        Logger class\n
        use it instead of 'print()'
    """
    def __init__(self, log_file: str = "server.log") -> None:
        colorama.init(autoreset=True)

        self._localdir = __file__.split('\\')[:-1]
        if self._localdir[0].endswith(':'): self._localdir[0] += '\\'
        self._localdir = os.path.join(*self._localdir)
        _logs_folder = os.path.join(self._localdir, "logs")
        if not os.path.isdir(_logs_folder):
            os.mkdir(_logs_folder)

        logging.basicConfig(
            filename=f'logs/{log_file}', filemode='a', format='[%(asctime)s] %(levelname)s : %(message)s')
        self._logger = logging.getLogger()

        self._warn_format = logging.Formatter(
            fmt=colorama.Fore.LIGHTBLACK_EX +'[%(asctime)s]' + colorama.Fore.YELLOW + '[%(levelname)s]:  %(message)s')
        self._error_format = logging.Formatter(
            fmt=colorama.Fore.LIGHTBLACK_EX +'[%(asctime)s]' + colorama.Fore.RED + '[%(levelname)s]:  %(message)s')
        self._success_format = logging.Formatter(
            fmt=colorama.Fore.LIGHTBLACK_EX +'[%(asctime)s]' + colorama.Fore.GREEN + '[%(levelname)s]: %(message)s')
        self._log_format = logging.Formatter(
            fmt=colorama.Fore.LIGHTBLACK_EX +'[%(asctime)s]' + colorama.Fore.LIGHTBLACK_EX + '[LOG]: %(message)s')
        self._debug_format = logging.Formatter(
            fmt=colorama.Fore.LIGHTBLACK_EX +'[%(asctime)s]' + colorama.Fore.BLUE + '[DEBUG]: %(message)s')

        self._logger.setLevel(logging.DEBUG)
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(logging.DEBUG)
        self._console_handler.setFormatter(self._log_format)

        self._logger.addHandler(self._console_handler)

    def log(self, message: str) -> None:
        """
            Log Text
            Color: White
        """
        self._console_handler.setFormatter(self._log_format)
        return self._logger.info(msg=message.strip())
    
    def debug(self, message: str) -> None:
        """
            Log Debug Text
            Color: Blue
        """
        self._console_handler.setFormatter(self._debug_format)
        return self._logger.info(msg=message.strip())

    def warn(self, message: str) -> None:
        """
            Warn Log
            Color: Yellow
        """
        self._console_handler.setFormatter(self._warn_format)
        return self._logger.warning(msg=message.strip())

    def error(self, message: str) -> None:
        """
            Error Log
            Color: Red
        """
        self._console_handler.setFormatter(self._error_format)
        return self._logger.error(msg=message.strip())

    def success(self, message: str) -> None:
        """
            Sucess Log
            Color: Green
        """
        self._console_handler.setFormatter(self._success_format)
        return self._logger.info(msg=message.strip())
