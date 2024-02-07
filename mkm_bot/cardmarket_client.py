from __future__ import annotations

import logging
import random
import re
import time
import undetected_chromedriver as uc

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from undetected_chromedriver.webelement import WebElement

from .common import PricingParameters
from .config import CardmarketConfig
from .pricing import compute_price

MKM_HOME = "https://cardmarket.com/en/Magic"
MKM_SINGLES = "https://cardmarket.com/en/Magic/Stock/Offers/Singles"

NAME_USERNAME = "username"
NAME_PASSWORD = "userPassword"
XPATH_LOGIN = "/html/body/header/nav/ul/li/div/form/input[@value='Log in']"
XPATH_LOGGEDIN_USERNAME = "/html/body/header/nav/ul/li/ul/li/a/div" \
    "[@title='My Account']/span[@class='d-none d-lg-block']"
XPATH_PAGE = "/html/body/main/div[@class='row g-0 flex-nowrap d-flex " \
    "align-items-center pagination mb-2 mt-2']/div[@class='col-12 col" \
    "-sm-6 ms-auto']/div/span"
XPATH_NEXT_PAGE = "/html/body/main/div[@class='row g-0 flex-nowrap d-" \
    "flex align-items-center pagination mb-2 mt-2']/div[@class='col-12 " \
    "col-sm-6 ms-auto']/div/a[@aria-label='Next page']"
XPATH_CARD_ROWS = "/html/body/main/div[@id='UserOffersTable']/" \
    "div[@class='table-body']/div[@class='row g-0 article-row']"
XPATH_CARD_URL = ".//div[@class='col-sellerProductInfo col']/div/div/a"
XPATH_EDIT_BUTTON = ".//div[@class='col-offer col-auto']/div[@class=" \
    "'actions-container d-flex align-items-center justify-content-end " \
    "col ps-2 pe-0']/div[@class='d-inline-flex']/div/a"
XPATH_PRICE_INPUT = "/html/body/div[@id='modal']/div/div/div" \
    "[@class='modal-body']/div/form//input[@name='price']"
XPATH_SUBMIT_PRICE_BUTTON = "/html/body/div[@id='modal']/div/div/div" \
    "[@class='modal-body']/div/form//button[@type='submit']"

logger = logging.getLogger(__name__)


def _short_delay() -> None:
    time.sleep(float(random.randrange(1, 500)) / 1000)
    return


def _medium_delay() -> None:
    time.sleep(float(random.randrange(450, 500)) / 100)
    return


def is_last_page(page_x_of_y: str) -> bool:
    match = re.match(r"Page (\d+) of (\d+)$", page_x_of_y)
    if match is None:
        raise RuntimeError(f"No match for '{page_x_of_y}'")

    current = int(match.group(1))
    total = int(match.group(2))

    if current > total or current == 0 or total == 0:
        raise RuntimeError(
            f"Invalid page numbers: current={current}, total={total}")

    return current == total


@dataclass
class CardRow:
    card_url: str
    edit_element: WebElement

    @classmethod
    def from_web_element(cls, card_row_element: WebElement) -> CardRow:
        card_url = card_row_element.find_element(
            By.XPATH, XPATH_CARD_URL
        ).get_attribute("href")

        edit_element = card_row_element.find_element(
            By.XPATH, XPATH_EDIT_BUTTON
        )

        return CardRow(card_url, edit_element)


class CardmarketClient:
    config: CardmarketConfig
    driver: uc.Chrome

    def __init__(self, config: CardmarketConfig) -> None:
        self.config = config

    def _open_driver(self) -> None:
        logger.info("Opening undetected_chromedriver.")

        chrome_options = Options()

        # to be able to open new tabs
        chrome_options.add_argument("--disable-popup-blocking")

        self.driver = uc.Chrome(
            options=chrome_options, headless=False, use_subprocess=True)

    def _close_driver(self) -> None:
        if hasattr(self, "driver"):
            logger.info("Closing undetected_chromedriver.")
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

    def update_card_prices(self) -> None:
        self.driver.get(MKM_SINGLES)
        logger.info(f"GET request to: {MKM_SINGLES}")
        _medium_delay()

        # Looping over pages
        while True:
            # Looping through the cards in a page here.
            for card_element in self.driver.find_elements(
                By.XPATH, XPATH_CARD_ROWS
            ):
                logger.info(f"card_element: {card_element}")
                card_row = CardRow.from_web_element(card_element)
                logger.info(f"card_row: {card_row}")

                parameters = self.get_pricing_parameters_for_card(card_row)

                new_price = compute_price(parameters)

                # Update the price of card
                self.update_single_price(new_price, card_row)

            page_x_of_y = self.driver.find_element(By.XPATH, XPATH_PAGE).text
            logger.info(f"Finished reading: {page_x_of_y}")
            if is_last_page(page_x_of_y):
                break

            self.driver.find_element(By.XPATH, XPATH_NEXT_PAGE).click()

    def get_pricing_parameters_for_card(
        self, card_row: CardRow
    ) -> PricingParameters:
        assert len(self.driver.window_handles) == 1, \
            "Unexpected window handle count before opening new window"

        logger.info(f"Opening tab for card with link: {card_row.card_url}")
        self.driver.execute_script(
            f"window.open('{card_row.card_url}');"
        )
        self.driver.switch_to.window(self.driver.window_handles[1])

        _medium_delay()
        time.sleep(3)
        # Obtain Pricing Parameters
        zero = Decimal(0)

        logger.info("Closing tab.")
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        assert len(self.driver.window_handles) == 1, \
            "Unexpected window handle count after closing the new window"
        _medium_delay()
        return PricingParameters(zero, zero, zero, zero, zero, zero)

    def update_single_price(self, price: Decimal, card_row: CardRow) -> None:
        card_row.edit_element.click()
        _medium_delay()

        rounded_price = str(round(price, 2))
        self.driver.find_element(By.XPATH, XPATH_PRICE_INPUT).clear()
        self.driver.find_element(By.XPATH, XPATH_PRICE_INPUT).send_keys(
            rounded_price
        )

        self.driver.find_element(By.XPATH, XPATH_SUBMIT_PRICE_BUTTON).click()
        _medium_delay()


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
