from lxml import etree
from lxml.objectify import ObjectifiedElement
from pathlib import Path


XSD_PATH = Path(__file__).parent / "mkm_bot.xsd"


def read_and_validate_xml_config(xml_path: Path) -> ObjectifiedElement:
    xsd: ObjectifiedElement
    xml: ObjectifiedElement

    with open(XSD_PATH, 'r') as fp_xsd:
        xsd = etree.XMLSchema(etree.parse(fp_xsd))
    with open(xml_path, 'r') as fp_xml:
        xml = etree.parse(fp_xml)

    xsd.assertValid(xml)
    return xml
