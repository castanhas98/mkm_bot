import logging
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
XPATH_LOGGEDIN_USERNAME = "/html/body/header/nav/ul/li/ul/li/a/div" \
    "[@title='My Account']/span[@class='d-none d-lg-block']"

logger = logging.getLogger(__name__)


def _short_delay() -> None:
    time.sleep(float(random.randrange(0, 30)) / 10)
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
        logger.info(f"GET request to: {self.config.endpoint}")
        _short_delay()

        self.driver.find_element(
            By.NAME, NAME_USERNAME
        ).send_keys(self.config.username)
        logger.info(f"Inserted username: {self.config.username}")
        _short_delay()

        self.driver.find_element(
            By.NAME, NAME_PASSWORD
        ).send_keys(self.config.password)
        logger.info("Inserted password")
        _short_delay()

        self.driver.find_element(
            By.XPATH, XPATH_LOGIN
        ).click()
        logger.info("Logged in")
        _short_delay()

        self._check_login_valid()

    def _check_login_valid(self) -> None:
        loggedin_username = self.driver.find_element(
            By.XPATH, XPATH_LOGGEDIN_USERNAME
        ).text

        if loggedin_username != self.config.username.upper():
            self._close_driver_and_throw(
                "Cannot find correct username after logging in. Expecting: "
                f"{self.config.username.capitalize()}. "
                f"Found: {loggedin_username}"
            )

        logger.info(
            "Successfully checked that username is as expected after login")

    def _close_driver_and_throw(self, reason: str) -> None:
        self._close_driver()
        raise RuntimeError(reason)


@contextmanager
def start_cardmarket_client(
    config: CardmarketConfig
) -> Iterator[CardmarketClient]:
    cardmarket_client = CardmarketClient(config)
    cardmarket_client._open_driver()

    yield cardmarket_client

    cardmarket_client._close_driver()
