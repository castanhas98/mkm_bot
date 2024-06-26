from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from lxml.objectify import ObjectifiedElement


def _read_line_from_file(file_path: Path) -> str:
    with open(file_path, 'r') as fp:
        return fp.readline().strip('\n')


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

        username = _read_line_from_file(username_path)
        password = _read_line_from_file(password_path)

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
class SmtpConfig:
    email_path: Path
    password_path: Path
    email: str
    password: str

    @classmethod
    def from_config(cls, xml_config: ObjectifiedElement) -> SmtpConfig:
        email_path = Path(xml_config.find("EmailPath").text)
        password_path = Path(xml_config.find("PasswordPath").text)

        email = _read_line_from_file(email_path)
        password = _read_line_from_file(password_path)

        return SmtpConfig(
            email_path=email_path,
            password_path=password_path,
            email=email,
            password=password,
        )

    def __repr__(self) -> str:
        return f"SmtpConfig(email_path={self.email_path}, " \
               f"password_path={self.password_path})"


@dataclass
class MkmBotConfig:
    logging_config: LoggingConfig
    cardmarket_config: CardmarketConfig
    smtp_config: SmtpConfig

    @classmethod
    def from_config(cls, xml_config: ObjectifiedElement) -> MkmBotConfig:
        logging_config = LoggingConfig(
            Path(xml_config.find("Logging").find("Directory").text)
        )

        cardmarket_config = CardmarketConfig.from_config(
            xml_config.find("Cardmarket")
        )

        smtp_config = SmtpConfig.from_config(
            xml_config.find("Smtp")
        )

        return MkmBotConfig(
            logging_config=logging_config,
            cardmarket_config=cardmarket_config,
            smtp_config=smtp_config,
        )
