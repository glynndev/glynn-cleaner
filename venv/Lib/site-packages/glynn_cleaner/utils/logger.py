USE_COLOUR = True

import logging
import logging.handlers
import os
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

# ------------------------------------------------------------
# Create logs directory if it doesn't exist
# ------------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ------------------------------------------------------------
# Per-run log file (unique for each execution)
# ------------------------------------------------------------
run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RUN_LOG_PATH = os.path.join(LOG_DIR, f"run_{run_timestamp}.log")

# ------------------------------------------------------------
# Rotating log file (long-term history)
# ------------------------------------------------------------
ROTATING_LOG_PATH = os.path.join(LOG_DIR, "cleaner_history.log")

# ------------------------------------------------------------
# Logger configuration
# ------------------------------------------------------------
logger = logging.getLogger("cleaner_logger")
logger.setLevel(logging.DEBUG)

# ------------------------------------------------------------
# Formatter
# ------------------------------------------------------------
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ------------------------------------------------------------
# Handlers
# ------------------------------------------------------------
run_handler = logging.FileHandler(RUN_LOG_PATH, encoding="utf-8")
run_handler.setLevel(logging.DEBUG)
run_handler.setFormatter(formatter)
logger.addHandler(run_handler)

rotating_handler = logging.handlers.RotatingFileHandler(
    ROTATING_LOG_PATH,
    maxBytes=1_000_000,
    backupCount=5,
    encoding="utf-8"
)
rotating_handler.setLevel(logging.INFO)
rotating_handler.setFormatter(formatter)
logger.addHandler(rotating_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ------------------------------------------------------------
# Colour-safe wrappers
# ------------------------------------------------------------
def _c(text, colour):
    """Return coloured text only if USE_COLOUR is True."""
    return f"{colour}{text}{Style.RESET_ALL}" if USE_COLOUR else text

# ------------------------------------------------------------
# Public helper functions
# ------------------------------------------------------------
def log_debug(message: str):
    logger.debug(_c(message, Fore.LIGHTBLACK_EX))

def log_info(message: str):
    logger.info(_c(message, Fore.CYAN))

def log_warning(message: str):
    logger.warning(_c(message, Fore.YELLOW))

def log_error(message: str):
    logger.error(_c(message, Fore.RED))

def log_critical(message: str):
    logger.critical(_c(message, Fore.MAGENTA + Style.BRIGHT))

def disable_colour():
    global USE_COLOUR
    USE_COLOUR = False



