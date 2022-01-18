import os
import glob
from lxml import etree
from jpylyzer.jpylyzer import checkFiles
from jpylyzer import config

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

checkFiles(config.INPUT_RECURSIVE_FLAG, True, testFiles)
