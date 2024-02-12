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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from undetected_chromedriver.webelement import WebElement

from .common import PricingParameters
from .config import CardmarketConfig
from .pricing import compute_price

TIMEOUT = 30
CLOUDFLARE_TAB_TITLE = 'Just a moment...'

MKM_HOME = "https://cardmarket.com/en/Magic"
MKM_SINGLES = "https://cardmarket.com/en/Magic/Stock/Offers/Singles"

NAME_USERNAME = "username"
NAME_PASSWORD = "userPassword"

XPATH_CLOUDFLARE_IFRAME = "//iframe[@title='Widget containing a " \
    "Cloudflare security challenge']"
XPATH_CLOUDFLARE_CHECKBOX = "//label[@class='ctp-checkbox-label']"
XPATH_LOGIN = "/html/body/header/nav/ul/li/div/form/input[@value='Log in']"
XPATH_LOGGEDIN_USERNAME = "/html/body/header/nav/ul/li/ul/li/a/div" \
    "[@title='My Account']/span[@class='d-none d-lg-block']"
XPATH_PAGE = "/html/body/main/div[@class='row g-0 flex-nowrap d-flex " \
    "align-items-center pagination mb-2 mt-2']/div[@class='col-12 col" \
    "-sm-6 ms-auto']/div/span"
XPATH_NEXT_PAGE = "/html/body/main/div[@class='row g-0 flex-nowrap " \
    "d-flex align-items-center pagination mt-3']/div[@class='col-12 " \
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
XPATH_PRICE_FROM = "//dt[contains(.,'From')]/following::dd"
XPATH_PRICE_TREND = "//dt[contains(.,'Price Trend')]/following::dd"
XPATH_PRICE_30 = "//dt[contains(.,'30-days average price')]/following::dd"
XPATH_PRICE_7 = "//dt[contains(.,'7-days average price')]/following::dd"
XPATH_PRICE_1 = "//dt[contains(.,'1-day average price')]/following::dd"

logger = logging.getLogger(__name__)


def _short_delay() -> None:
    time.sleep(float(random.randrange(1, 500)) / 1000)
    return


def _medium_delay() -> None:
    time.sleep(float(random.randrange(1000, 1500)) / 100)
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


def get_price_from_string(price_str: str) -> Decimal:
    match = re.match(r"^(\d+,\d{2}) €$", price_str)
    if match is None:
        raise RuntimeError(f"No match for '{price_str}'")

    price_str_no_eur = match.group(1)
    price = Decimal(price_str_no_eur.replace(',', '.'))

    if price == Decimal(0):
        raise RuntimeError(f"Price ({price}) is Zero!: {price_str}")

    return price


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
    actions: ActionChains

    def __init__(self, config: CardmarketConfig) -> None:
        self.config = config

    def _open_driver(self) -> None:
        logger.info("Opening undetected_chromedriver.")

        chrome_options = Options()

        # to be able to open new tabs
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--auto-open-devtools-for-tabs")

        self.driver = uc.Chrome(
            options=chrome_options, headless=False, use_subprocess=True)

        self.actions = ActionChains(self.driver)

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

        while True:
            for card_element in self.driver.find_elements(
                By.XPATH, XPATH_CARD_ROWS
            ):
                self.actions.move_to_element(card_element).perform()

                logger.info(f"card_element: {card_element}")
                card_row = CardRow.from_web_element(card_element)
                logger.info(f"card_row: {card_row}")

                parameters = self.get_pricing_parameters_for_card(card_row)

                new_price = compute_price(parameters)

                self.update_single_price(new_price, card_row)

            page_x_of_y = self.driver.find_element(By.XPATH, XPATH_PAGE).text
            logger.info(f"Finished reading: {page_x_of_y}")
            if is_last_page(page_x_of_y):
                break

            next_page_element = self.driver.find_element(
                By.XPATH, XPATH_NEXT_PAGE
            )
            self.actions.scroll_to_element(next_page_element).perform()
            next_page_element.click()
            _medium_delay()

    def get_pricing_parameters_for_card(
        self, card_row: CardRow
    ) -> PricingParameters:
        assert len(self.driver.window_handles) == 2, \
            "Unexpected window handle count before opening new window"

        logger.info(f"Opening tab for card with link: {card_row.card_url}")
        self.driver.execute_script(
            f"window.open('{card_row.card_url}', '_blank');"
        )
        self.driver.switch_to.window(self.driver.window_handles[-1])
        _medium_delay()

        # Obtain Pricing Parameters
        from_price = self.driver.find_element(By.XPATH, XPATH_PRICE_FROM).text
        tren_price = self.driver.find_element(By.XPATH, XPATH_PRICE_TREND).text
        thirty_price = self.driver.find_element(By.XPATH, XPATH_PRICE_30).text
        seven_price = self.driver.find_element(By.XPATH, XPATH_PRICE_7).text
        one_price = self.driver.find_element(By.XPATH, XPATH_PRICE_1).text

        pricing_parameters = PricingParameters(
            from_price=get_price_from_string(from_price),
            trend_price=get_price_from_string(tren_price),
            thirty_price=get_price_from_string(thirty_price),
            seven_price=get_price_from_string(seven_price),
            one_price=get_price_from_string(one_price)
        )
        logger.info(f"Produced pricing parameters: {pricing_parameters}")

        logger.info("Closing tab.")
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        assert len(self.driver.window_handles) == 2, \
            "Unexpected window handle count after closing the new window"
        _medium_delay()

        return pricing_parameters

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
