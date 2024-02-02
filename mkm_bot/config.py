from dataclasses import dataclass
from pathlib import Path
from lxml.objectify import ObjectifiedElement


@dataclass
class LoggingConfig:
    directory: Path


@dataclass
class DataProviderConfig:
    endpoint: str

    def __init__(self, xml_config: ObjectifiedElement) -> None:
        self.endpoint = xml_config.find("Endpoint").text


@dataclass
class MkmBotConfig:
    data_provider_config: DataProviderConfig
    logging_config: LoggingConfig

    def __init__(self, xml_config: ObjectifiedElement) -> None:
        self.logging_config = LoggingConfig(
            Path(xml_config.find("Logging").find("Directory").text)
        )
        self.data_provider_config = DataProviderConfig(
            xml_config.find("DataProvider")
        )
