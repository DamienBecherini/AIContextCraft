import logging
import os

from rich.console import Console
from rich.logging import RichHandler

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def setup_logging(log_file_path, verbose, quiet=False, enable_file_logging=True):
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    if enable_file_logging and log_file_path is not None:
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    disable_color = bool(os.environ.get("NO_COLOR")) or not os.isatty(2)
    console = Console(stderr=True, no_color=disable_color)
    console_handler = RichHandler(
        console=console,
        show_time=False,
        show_path=False,
        rich_tracebacks=False,
        markup=False,
    )
    if quiet:
        console_level = logging.ERROR
    elif verbose:
        console_level = logging.INFO
    else:
        console_level = logging.WARNING
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console_handler)


def format_bytes(size):
    if size < 1024:
        return f"{size} B"
    for unit in ['KB', 'MB', 'GB', 'TB']:
        size /= 1024.0
        if size < 1024.0:
            return f"{size:.2f} {unit}"
    return f"{size:.2f} PB"


def get_file_stats(content_str, encoding='utf-8'):
    total_bytes = len(content_str.encode(encoding))
    formatted_size = format_bytes(total_bytes)
    tokens = "N/A"
    if TIKTOKEN_AVAILABLE:
        try:
            encoding_tiktoken = tiktoken.get_encoding("cl100k_base")
            tokens = len(encoding_tiktoken.encode(content_str))
        except Exception as e:
            logging.error(f"Erreur Tiktoken : {e}")
            tokens = "Erreur"
    return f"Taille: {formatted_size} ({total_bytes:,} octets), Tokens (estim.): {tokens}"
