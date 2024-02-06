from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from lxml.objectify import ObjectifiedElement


@dataclass
class LoggingConfig:
    directory: Path


@dataclass
class CardmarketConfig:
    username_path: Path
    password_path: Path
    username: str
    password: str

    @classmethod
    def from_config(cls, xml_config: ObjectifiedElement) -> CardmarketConfig:
        username_path = Path(xml_config.find("UsernamePath").text)
        password_path = Path(xml_config.find("PasswordPath").text)

        username: str
        with open(username_path, 'r') as fp_username:
            username = fp_username.readline().strip('\n')

        password: str
        with open(password_path, 'r') as fp_password:
            password = fp_password.readline().strip('\n')

        return CardmarketConfig(
            username_path=username_path,
            password_path=password_path,
            username=username,
            password=password,
        )

    def __repr__(self) -> str:
        return f"CardmarketConfig(username_path={self.username_path}, " \
               f"password_path={self.password_path})"


@dataclass
class MkmBotConfig:
    logging_config: LoggingConfig
    cardmarket_config: CardmarketConfig

    @classmethod
    def from_config(cls, xml_config: ObjectifiedElement) -> MkmBotConfig:
        logging_config = LoggingConfig(
            Path(xml_config.find("Logging").find("Directory").text)
        )

        cardmarket_config = CardmarketConfig.from_config(
            xml_config.find("Cardmarket")
        )

        return MkmBotConfig(
            logging_config=logging_config,
            cardmarket_config=cardmarket_config,
        )
