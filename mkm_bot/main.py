import sys

from pathlib import Path
from .xsd.xml_config import read_and_validate_xml_config
from .config import MkmBotConfig


def main() -> None:
    assert len(sys.argv) == 2

    xml_path = Path(sys.argv[1])
    assert xml_path.exists()

    xml_root = read_and_validate_xml_config(xml_path)
    mkm_bot_config = MkmBotConfig(xml_root)
    print(mkm_bot_config)
    return


if __name__ == '__main__':
    main()
