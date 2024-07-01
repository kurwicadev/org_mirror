import argparse
import logging

from dotenv import load_dotenv


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cron", action="store_true")
parser.add_argument("-o", "--org", required=True, action="append")

args = parser.parse_args()

handlers = [
    logging.FileHandler(f"{__name__}.log", encoding="utf-8")
]

if not args.cron:
    handlers.append(logging.StreamHandler())

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    handlers=handlers
)
log = logging.getLogger(__name__)

load_dotenv()
