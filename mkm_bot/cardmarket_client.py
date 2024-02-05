import logging
import random
import re
import time
import undetected_chromedriver as uc

from decimal import Decimal
from typing import Iterator
from contextlib import contextmanager
from selenium.webdriver.common.by import By

from .common import PricingParameters
from .config import CardmarketConfig

MKM_HOME = "https://cardmarket.com/en/Magic"
MKM_SINGLES = "https://cardmarket.com/en/Magic/Stock/Offers/Singles"

NAME_USERNAME = "username"
NAME_PASSWORD = "userPassword"
XPATH_LOGIN = "/html/body/header/nav/ul/li/div/form/input[@value='Log in']"
XPATH_LOGGEDIN_USERNAME = "/html/body/header/nav/ul/li/ul/li/a/div" \
    "[@title='My Account']/span[@class='d-none d-lg-block']"
XPATH_PAGE = "/html/body/main/div[@class='row g-0 flex-nowrap d-flex align-items-center pagination mb-2 mt-2']/div[@class='col-12 col-sm-6 ms-auto']/div/span"
XPATH_NEXT_PAGE = "/html/body/main/div[@class='row g-0 flex-nowrap d-flex align-items-center pagination mb-2 mt-2']/div[@class='col-12 col-sm-6 ms-auto']/div/a[@aria-label='Next page']"


logger = logging.getLogger(__name__)


def _medium_delay() -> None:
    time.sleep(float(random.randrange(0, 300)) / 100)
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
        self.driver.get(MKM_HOME)
        logger.info(f"GET request to: {MKM_HOME}")
        _medium_delay()

        self.driver.find_element(
            By.NAME, NAME_USERNAME
        ).send_keys(self.config.username)
        logger.info(f"Inserted username: {self.config.username}")
        _medium_delay()

        self.driver.find_element(
            By.NAME, NAME_PASSWORD
        ).send_keys(self.config.password)
        logger.info("Inserted password")
        _medium_delay()

        self.driver.find_element(
            By.XPATH, XPATH_LOGIN
        ).click()
        logger.info("Logged in")
        _medium_delay()

        self._check_login_valid()

    def _check_login_valid(self) -> None:
        loggedin_username = self.driver.find_element(
            By.XPATH, XPATH_LOGGEDIN_USERNAME
        ).text

        if loggedin_username != self.config.username.upper():
            raise RuntimeError(
                "Cannot find correct username after logging in. Expecting: "
                f"{self.config.username.capitalize()}. "
                f"Found: {loggedin_username}"
            )

        logger.info(
            "Successfully checked that username is as expected after login")

    def _is_last_page(self, page_x_of_y: str) -> bool:
        match = re.match(r"Page (\d+) of (\d+)", page_x_of_y)
        if match is None:
            raise RuntimeError(f"No match for '{page_x_of_y}'")

        current = int(match.group(1))
        total = int(match.group(2))

        if current > total or current <= 0 or total <= 0:
            raise RuntimeError(
                f"Invalid page numbers: current={current}, total={total}")

        return current == total

    def get_pricing_parameters(self) -> Iterator[PricingParameters]:
        self.driver.get(MKM_SINGLES)
        logger.info(f"GET request to: {MKM_SINGLES}")
        _medium_delay()

        page_x_of_y = self.driver.find_element(By.XPATH, XPATH_PAGE).text

        while not self._is_last_page(page_x_of_y):
            self.driver.find_element(By.XPATH, XPATH_NEXT_PAGE).click()
            _medium_delay()

            zero = Decimal(0)
            yield PricingParameters(zero, zero, zero, zero, zero, zero)


@contextmanager
def start_cardmarket_client(
    config: CardmarketConfig
) -> Iterator[CardmarketClient]:
    cardmarket_client = CardmarketClient(config)
    cardmarket_client._open_driver()

    try:
        yield cardmarket_client
    except Exception as e:
        logger.error(e)
    finally:
        cardmarket_client._close_driver()
