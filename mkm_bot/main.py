import sys
import lxml
import __main__

from pathlib import Path
from lxml import etree


def read_and_validate_xml_config(xml_path: Path) -> etree:
    lxml.etree.parse(xml_path)

    # assert hasattr(__main__, __file__)  # need to figure out how to do this properly
    xsd_path = Path(__main__.__file__)
    xsd: lxml.etree
    with open(xsd_path, 'r') as fp:
        xsd = etree.XMLSchema(etree.parse(fp))
    with open(xml_path, 'r') as fp:
        xml = lxml.etree.parse(fp)

    xsd.assertValid(xml)


def main() -> None:
    # assert sys.argc == 2
    print(__main__.__file__)
    xml_root = read_and_validate_xml_config(sys.argv[1])
    print('Hello, World!')
    print(sys.argv[0])
    return


if __name__ == '__main__':
    main()
