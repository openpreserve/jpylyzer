import os
import glob
from pathlib import Path
from lxml import etree
from jpylyzer.jpylyzer import checkFiles
from jpylyzer import config

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

xsdFile = os.path.join(os.path.split(os.path.split(SCRIPT_DIR)[0])[0],
                       "xsd/jpylyzer-v-2-1.xsd")

print(xsdFile)

xsdFile = "/home/johan/jpylyzer/xsd/jpylyzer-v-2-1.xsd"
xmlOut = "/home/johan/test/all-21.xml"

# Directory with test files
testFilesDir = "/home/johan/jpylyzer-test-files/"

# All files in test files dir, excluding .md file
testFiles = glob.glob(os.path.join(testFilesDir, '*[!.md]'))

def validatefromfile():
    # Parse XSD schema
    xmlschema_doc = etree.parse(xsdFile)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # Parse XML
    xml_doc = etree.parse(xmlOut)
    result = xmlschema.validate(xml_doc)
    print(result)

