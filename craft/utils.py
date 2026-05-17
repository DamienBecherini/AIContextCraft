import logging

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def setup_logging(log_file_path, verbose):
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if verbose else logging.WARNING)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
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
