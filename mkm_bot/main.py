import logging
import os
import sys

from datetime import datetime
from pathlib import Path
from .xsd.xml_config import read_and_validate_xml_config
from .config import MkmBotConfig, LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    os.makedirs(config.directory, exist_ok=True)
    file_name = datetime.now().strftime("%Y%m%d_%H%M%S_mkm_bot.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-4s]: %(message)s",
        datefmt="%d/%m/%y %H:%M:%S",
        filename=config.directory / file_name
    )


def main() -> None:
    assert len(sys.argv) == 2

    xml_path = Path(sys.argv[1])
    assert xml_path.exists()

    xml_root = read_and_validate_xml_config(xml_path)
    mkm_bot_config = MkmBotConfig(xml_root)

    setup_logging(mkm_bot_config.logging_config)
    logging.info("Successfully read XML config: %s", mkm_bot_config)
    return


if __name__ == '__main__':
    main()
