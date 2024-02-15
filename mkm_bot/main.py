import logging
import os
import sys

from datetime import datetime
from pathlib import Path
from typing import Optional

from .cardmarket_client import start_cardmarket_client
from .config import MkmBotConfig, LoggingConfig
from .smtp import send_email_report
from .xsd.xml_config import read_and_validate_xml_config


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
    # Read config and set up logging
    assert len(sys.argv) == 2

    xml_path = Path(sys.argv[1])
    assert xml_path.exists()

    xml_root = read_and_validate_xml_config(xml_path)
    mkm_bot_config = MkmBotConfig.from_config(xml_root)

    setup_logging(mkm_bot_config.logging_config)
    logger = logging.getLogger(__name__)

    logger.info("Successfully read XML config: %s", mkm_bot_config)

    exception: Optional[Exception] = None
    try:
        with start_cardmarket_client(
            mkm_bot_config.cardmarket_config
        ) as cardmarket_client:
            cardmarket_client.login()

            cardmarket_client.update_card_prices(are_foil=False)
            cardmarket_client.update_card_prices(are_foil=True)

    except Exception as e:
        exception = e

    send_email_report(mkm_bot_config.smtp_config, exception)

    logger.info("Done. Shutting down.")
    return


if __name__ == '__main__':
    main()
