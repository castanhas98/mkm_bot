import random
import time
import undetected_chromedriver as uc

from typing import Iterator
from contextlib import contextmanager
from selenium.webdriver.common.by import By

from .config import CardmarketConfig

NAME_USERNAME = "username"
NAME_PASSWORD = "userPassword"
XPATH_LOGIN = "/html/body/header/nav/ul/li/div/form/input[@value='Log in']"


def _short_delay() -> None:
    time.sleep(float(random.randrange(0, 50)) / 10)
    return


class CardmarketClient:
    config: CardmarketConfig
    driver: uc.Chrome

    def __init__(self, config: CardmarketConfig) -> None:
        self.config = config

    def __del__(self) -> None:
        self._close_driver()

    def _open_driver(self) -> None:
        self.driver = uc.Chrome(headless=False, use_subprocess=False)

    def _close_driver(self) -> None:
        self.driver.quit()

    def login(self) -> None:
        self.driver.get(self.config.endpoint)
        _short_delay()

        self.driver.find_element(
            By.NAME, NAME_USERNAME
        ).send_keys(self.config.username)
        _short_delay()

        self.driver.find_element(
            By.NAME, NAME_PASSWORD
        ).send_keys(self.config.password)
        _short_delay()

        self.driver.find_element(
            By.XPATH, XPATH_LOGIN
        ).click()
        _short_delay()


@contextmanager
def start_cardmarket_client(
    config: CardmarketConfig
) -> Iterator[CardmarketClient]:
    cardmarket_client = CardmarketClient(config)
    cardmarket_client._open_driver()

    yield cardmarket_client

    cardmarket_client._close_driver()
