import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter to add colors to log levels.
    """
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger(log_file="app", log_level=logging.INFO):
    """
    Sets up a logger that logs messages to both the console and a log file.

    Args:
        log_file (str): The path to the log file.
        log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
    """
    # Create a logger
    logger = logging.getLogger("mo")
    logger.setLevel(log_level)

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_file + ".log")
    file_handler.setLevel(log_level)

    # Create a file handler for logging to a file
    err_file_handler = logging.FileHandler(log_file + ".error.log")
    err_file_handler.setLevel(logging.ERROR)

    # Create a console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Define a standard log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    colored_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Set formatters for handlers
    file_handler.setFormatter(formatter)
    err_file_handler.setFormatter(formatter)
    console_handler.setFormatter(colored_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(err_file_handler)
    logger.addHandler(console_handler)

    return logger

# Example usage
if __name__ == "__main__":
    logger = setup_logger()
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

