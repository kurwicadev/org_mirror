import logging


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"{__name__}.log", encoding="utf-8")
    ]
)
log = logging.getLogger(__name__)
