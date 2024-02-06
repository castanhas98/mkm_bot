from pathlib import Path

from mkm_bot.cardmarket_client import CardmarketClient
from mkm_bot.config import CardmarketConfig


USERNAME_PATH = Path("/path/to/username")
PASSWORD_PATH = Path("/path/to/password")
USERNAME = "username"
PASSWORD = "password"

CARDMARKET_CONFIG = CardmarketConfig(
    username_path=USERNAME_PATH,
    password_path=PASSWORD_PATH,
    username=USERNAME,
    password=PASSWORD
)
CARDMARKET_CLIENT = CardmarketClient(CARDMARKET_CONFIG)
