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

    def __init__(self, xml_config: ObjectifiedElement) -> None:
        self.username_path = Path(xml_config.find("UsernamePath").text)
        self.password_path = Path(xml_config.find("PasswordPath").text)

        with open(self.username_path, 'r') as fp_username:
            self.username = fp_username.readline().strip('\n')

        with open(self.password_path, 'r') as fp_password:
            self.password = fp_password.readline().strip('\n')

    def __repr__(self) -> str:
        return f"CardmarketConfig(username_path={self.username_path}, " \
               f"password_path={self.password_path})"


@dataclass
class MkmBotConfig:
    cardmarket_config: CardmarketConfig
    logging_config: LoggingConfig

    def __init__(self, xml_config: ObjectifiedElement) -> None:
        self.logging_config = LoggingConfig(
            Path(xml_config.find("Logging").find("Directory").text)
        )
        self.cardmarket_config = CardmarketConfig(
            xml_config.find("Cardmarket")
        )
