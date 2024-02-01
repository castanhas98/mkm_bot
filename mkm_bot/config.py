from dataclasses import dataclass
from lxml.objectify import ObjectifiedElement


@dataclass
class DataProviderConfig:
    endpoint: str

    def __init__(self, xml_config: ObjectifiedElement) -> None:
        self.endpoint = xml_config.find("Endpoint").text


@dataclass
class MkmBotConfig:
    data_provider_config: DataProviderConfig

    def __init__(self, xml_config: ObjectifiedElement) -> None:
        self.data_provider_config = DataProviderConfig(
            xml_config.find("DataProvider")
        )
