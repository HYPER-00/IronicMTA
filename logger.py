from typing import Dict, Any
import logging
import logging.handlers
import re
import socket
import sys


class ColorCodes:
    grey = "\x1b[38;21m"
    green = "\x1b[1;32m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    purple = "\x1b[1;35m"
    reset = "\x1b[0m"


class ColorizedArgsFormatter(logging.Formatter):
    arg_colors = [ColorCodes.purple, ColorCodes.light_blue]
    level_fields = ["levelname", "levelno"]
    level_to_color = {
        logging.DEBUG: ColorCodes.grey,
        logging.INFO: ColorCodes.green,
        logging.WARNING: ColorCodes.yellow,
        logging.ERROR: ColorCodes.red,
        logging.CRITICAL: ColorCodes.bold_red,
    }

    def __init__(self, fmt: str):
        super().__init__()
        self.level_to_formatter: Dict[int, logging.Formatter] = {}
        self._format = fmt

        self.add_color_format(logging.DEBUG)
        self.add_color_format(logging.INFO)
        self.add_color_format(logging.WARNING)
        self.add_color_format(logging.ERROR)
        self.add_color_format(logging.CRITICAL)

    def add_color_format(self, level: int):
        color = ColorizedArgsFormatter.level_to_color[level]
        for fld in ColorizedArgsFormatter.level_fields:
            search = f"(%\({fld}\).*?s)"
            _format = re.sub(search, f"{color}\\1{ColorCodes.reset}", self._format)
        formatter = logging.Formatter(self._format)
        self.level_to_formatter[level] = formatter

    @staticmethod
    def rewrite_record(record: logging.LogRecord):
        if not BraceFormatStyleFormatter.is_brace_format_style(record):
            return

        msg = record.msg
        msg = msg.replace("{", "_{{")
        msg = msg.replace("}", "_}}")
        placeholder_count = 0
        # add ANSI escape code for next alternating color before each formatting parameter
        # and reset color after it.
        while True:
            if "_{{" not in msg:
                break
            color_index = placeholder_count % len(ColorizedArgsFormatter.arg_colors)
            color = ColorizedArgsFormatter.arg_colors[color_index]
            msg = msg.replace("_{{", color + "{", 1)
            msg = msg.replace("_}}", "}" + ColorCodes.reset, 1)
            placeholder_count += 1

        record.msg = msg.format(*record.args)
        record.args = []

    def format(self, record):
        orig_msg = record.msg
        orig_args = record.args
        formatter = self.level_to_formatter.get(record.levelno)
        self.rewrite_record(record)
        formatted = formatter.format(record)
        record.msg = orig_msg
        record.args = orig_args
        return formatted


class BraceFormatStyleFormatter(logging.Formatter):
    def __init__(self, fmt: str):
        super().__init__()
        self.formatter = logging.Formatter(fmt)

    @staticmethod
    def is_brace_format_style(record: logging.LogRecord):
        if len(record.args) == 0:
            return False

        msg = record.msg
        if "%" in msg:
            return False

        count_of_start_param = msg.count("{")
        count_of_end_param = msg.count("}")

        if count_of_start_param != count_of_end_param:
            return False

        if count_of_start_param != len(record.args):
            return False

        return True

    @staticmethod
    def rewrite_record(record: logging.LogRecord):
        if not BraceFormatStyleFormatter.is_brace_format_style(record):
            return

        record.msg = record.msg.format(*record.args)
        record.args = []

    def format(self, record):
        orig_msg = record.msg
        orig_args = record.args
        self.rewrite_record(record)
        formatted = self.formatter.format(record)

        # restore log record to original state for other handlers
        record.msg = orig_msg
        record.args = orig_args
        return formatted


class Logger(logging.Logger):
    def __init__(self, name: str, level: int = 0) -> None:
        super().__init__(__name__, level)
        self.setLevel(logging.DEBUG)
        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setLevel("DEBUG")
        self._console_handler.setFormatter(
            ColorizedArgsFormatter(
                "%(asctime)s - %(levelname)-8s - %(name)-25s - %(message)s"
            )
        )
        self.addHandler(self._console_handler)
        
        file_handler = logging.FileHandler("app.log")
        file_level = "DEBUG"
        file_handler.setLevel(file_level)
        file_format = "%(asctime)s - %(name)s (%(lineno)s) - %(levelname)-8s - %(threadName)-12s - %(message)s"
        file_handler.setFormatter(BraceFormatStyleFormatter(file_format))
        self.addHandler(file_handler)


logger = Logger("test")
logger.info("Hello World")
logger.info("Request from {} handled in {:.3f} ms", socket.gethostname(), 11)
logger.info("Request from {} handled in {:.3f} ms", "127.0.0.1", 33.1)
logger.info("My favorite drinks are {}, {}, {}, {}", "milk", "wine", "tea", "beer")
logger.debug("this is a {} message", logging.getLevelName(logging.DEBUG))
logger.info("this is a {} message", logging.getLevelName(logging.INFO))
logger.warning("this is a {} message", logging.getLevelName(logging.WARNING))
logger.error("this is a {} message", logging.getLevelName(logging.ERROR))
logger.critical("this is a {} message", logging.getLevelName(logging.CRITICAL))
logger.info("Does old-style formatting also work? %s it is, but no colors (yet)", True)
