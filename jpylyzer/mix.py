"""Mix Property class to generate the mix property."""
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re
from . import etpatch as ET


class Mix:
    """Class for generating NISO MIX image metadata."""

    def __init__(self, mixFlag):
        """Initialise the Mix instance with a mixFlag."""
        self.mixFlag = mixFlag

    def generateMixBasicDigitalObjectInformation(self, properties):
        """Generate a mix BasicDigitalObjectInformation."""
        mixBdoi = ET.Element('mix:BasicDigitalObjectInformation')

        mixFormatDesignation = ET.Element('mix:FormatDesignation')
        br = properties.find('fileTypeBox/br')
        if br is None:
            formatName = 'image/jp2'
        else:
            value = br.text
            formatName = 'image/' + value.strip()
        mixFormatDesignation.appendChildTagWithText(
            'mix:formatName', formatName)
        mixBdoi.append(mixFormatDesignation)
        if self.mixFlag == 1:
            mixBdoi.appendChildTagWithText('mix:byteOrder', 'big_endian')
        else:
            mixBdoi.appendChildTagWithText('mix:byteOrder', 'big endian')

        mixComp = ET.Element('mix:Compression')
        compression = properties.find(
            'contiguousCodestreamBox/cod/transformation').text
        if compression == '5-3 reversible':
            compressionScheme = 'JPEG 2000 Lossless'
        else:
            compressionScheme = 'JPEG 2000 Lossy'
        mixComp.appendChildTagWithText(
            'mix:compressionScheme', compressionScheme)
        if self.mixFlag == 1:
            # compressionRatio is a int in mix 1...
            compressionRatio = int(
                round(
                    float(
                        properties.find('compressionRatio').text),
                    0))
            mixComp.appendChildTagWithText(
                'mix:compressionRatio', str(compressionRatio))
        else:
            # compressionRatio is a Rational in mix 2.0 (keep only 2 digits)
            value = int(
                round(
                    float(
                        properties.find('compressionRatio').text) *
                    100,
                    0))
            mixCompRatio = ET.Element('mix:compressionRatio')
            mixCompRatio.appendChildTagWithText('mix:numerator', str(value))
            mixCompRatio.appendChildTagWithText('mix:denominator', '100')
            mixComp.append(mixCompRatio)
        mixBdoi.append(mixComp)

        return mixBdoi

    def generateMixBasicImageInformation(self, properties):
        """Generate a mix BasicImageInformation."""
        mixBio = ET.Element('mix:BasicImageInformation')
        mixBic = ET.Element('mix:BasicImageCharacteristics')
        width = str(properties.find('jp2HeaderBox/imageHeaderBox/width').text)
        height = str(properties.find(
            'jp2HeaderBox/imageHeaderBox/height').text)
        mixBic.appendChildTagWithText('mix:imageWidth', width)
        mixBic.appendChildTagWithText('mix:imageHeight', height)
        # Try ICC first
        iccElement = properties.find('jp2HeaderBox/colourSpecificationBox/icc')
        if iccElement:
            mixPI = ET.Element('mix:PhotometricInterpretation')
            colorSpace = properties.find(
                'jp2HeaderBox/colourSpecificationBox/icc/colourSpace').text
            mixPI.appendChildTagWithText('mix:colorSpace', colorSpace.strip())
            iccProfile = properties.find(
                'jp2HeaderBox/colourSpecificationBox/icc/description').text
            mixColorProfile = ET.Element('mix:ColorProfile')
            mixIccProfile = ET.Element('mix:IccProfile')
            mixIccProfile.appendChildTagWithText(
                'mix:iccProfileName', iccProfile)
            mixColorProfile.append(mixIccProfile)
            mixPI.append(mixColorProfile)
            mixBic.append(mixPI)
        else:
            mixPI = ET.Element('mix:PhotometricInterpretation')
            colorSpace = properties.find(
                'jp2HeaderBox/colourSpecificationBox/enumCS').text
            mixPI.appendChildTagWithText('mix:colorSpace', colorSpace.strip())
            mixBic.append(mixPI)
        mixBio.append(mixBic)

        mixSFC = ET.Element('mix:SpecialFormatCharacteristics')
        mixJP2 = ET.Element('mix:JPEG2000')
        comment = properties.find('contiguousCodestreamBox/com/comment')
        if comment is not None:
            commentText = comment.text
            m = re.search(r'(.*)-v([0-9\.]*)', commentText)
            if m:
                # generate CodecCompliance only if it matches the regex
                mixCodecCompliance = ET.Element('mix:CodecCompliance')
                mixCodecCompliance.appendChildTagWithText(
                    'mix:codec', m.group(1))
                mixCodecCompliance.appendChildTagWithText(
                    'mix:codecVersion', m.group(2))
                mixJP2.append(mixCodecCompliance)
        mixEncodingOptions = ET.Element('mix:EncodingOptions')
        tilesX = properties.find('contiguousCodestreamBox/siz/xTsiz').text
        tilesY = properties.find('contiguousCodestreamBox/siz/yTsiz').text
        if self.mixFlag == 1:
            tilesString = str(tilesX) + 'x' + str(tilesY)
            mixEncodingOptions.appendChildTagWithText('mix:tiles', tilesString)
        else:
            mixTiles = ET.Element('mix:Tiles')
            mixTiles.appendChildTagWithText('mix:tileWidth', str(tilesX))
            mixTiles.appendChildTagWithText('mix:tileHeight', str(tilesY))
            mixEncodingOptions.append(mixTiles)

        layers = properties.find('contiguousCodestreamBox/cod/layers').text
        if str(layers) != "0":
            mixEncodingOptions.appendChildTagWithText(
                'mix:qualityLayers', str(layers))
        levels = properties.find('contiguousCodestreamBox/cod/levels').text
        if str(levels) != "0":
            mixEncodingOptions.appendChildTagWithText(
                'mix:resolutionLevels', str(levels))

        mixJP2.append(mixEncodingOptions)
        mixSFC.append(mixJP2)
        mixBio.append(mixSFC)
        return mixBio

    @staticmethod
    def findValueInRDF(prop, prefixPath, ns, tag):
        """Find a value in RDF : first as an element then as an attribute."""
        path = prefixPath + "/" + ns + tag
        value = prop.find(path)
        if value is not None:
            return value.text

        value = prop.find(prefixPath).attrib.get(ns + tag, None)
        if value and value is not None:
            return value
        return None

    @staticmethod
    def addIfExist(prop, prefixPath, ns, tag, destEl, destTagName):
        """Look for a value in RDF and build a element, if found."""
        value = Mix.findValueInRDF(prop, prefixPath, ns, tag)
        if value is not None:
            destEl.appendChildTagWithText(destTagName, value.strip())
            return True
        return False

    def generateMixImageCaptureMetadata(self, properties):
        """Generate a mix ImageCaptureMetadata."""
        if self.mixFlag == 0:
            # Avoid a static method using self
            return None

        mixIcm = ET.Element('mix:ImageCaptureMetadata')
        rdfBox = properties.find('xmlBox/{adobe:ns:meta/}xmpmeta/'
                                 '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
        if not rdfBox:
            rdfBox = properties.find('uuidBox/{adobe:ns:meta/}xmpmeta/'
                                     '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
        if not rdfBox:
            return None
        mixGci = ET.Element('mix:GeneralCaptureInformation')
        Mix.addIfExist(rdfBox,
                       '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                       '{http://ns.adobe.com/xap/1.0/}', 'CreateDate',
                       mixGci,
                       'mix:dateTimeCreated')
        Mix.addIfExist(rdfBox, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                       '{http://ns.adobe.com/tiff/1.0/}',
                       'Artist',
                       mixGci,
                       'mix:imageProducer')
        mixIcm.append(mixGci)
        fillSc = False
        mixSc = ET.Element('mix:ScannerCapture')
        fillSc = Mix.addIfExist(rdfBox,
                                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                '{http://ns.adobe.com/tiff/1.0/}',
                                'Make',
                                mixSc,
                                'mix:scannerManufacturer') or fillSc
        fillSm = False
        mixSm = ET.Element('mix:ScannerModel')
        fillSm = Mix.addIfExist(rdfBox,
                                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                '{http://ns.adobe.com/tiff/1.0/}',
                                'Model',
                                mixSm,
                                'mix:scannerModelName')
        fillSm = Mix.addIfExist(rdfBox,
                                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                '{http://ns.adobe.com/exif/1.0/aux/}',
                                'SerialNumber',
                                mixSm,
                                'mix:scannerModelSerialNo') or fillSm
        if fillSm:
            mixSc.append(mixSm)
            fillSc = True

        creatorTool = Mix.findValueInRDF(rdfBox,
                                         '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                         '{http://ns.adobe.com/xap/1.0/}',
                                         'CreatorTool')
        if creatorTool is not None:
            mixSss = ET.Element('mix:ScanningSystemSoftware')
            m = re.search(r'^(.*) ([0-9\.]*)$', creatorTool)
            if m:
                mixSss.appendChildTagWithText(
                    'mix:scanningSoftwareName', m.group(1))
                mixSss.appendChildTagWithText(
                    'mix:scanningSoftwareVersionNo', m.group(2))
            else:
                mixSss.appendChildTagWithText(
                    'mix:scanningSoftwareName', creatorTool)
            mixSc.append(mixSss)
            fillSc = True

        if fillSc:
            mixIcm.append(mixSc)

        return mixIcm

    def generateMixImageAssessmentMetadata(self, properties):
        """Generate a mix ImageAssessmentMetadata."""
        mixIam = ET.Element('mix:ImageAssessmentMetadata')

        # Get the resolution in the captureResolutionBox first
        resolutionBox = properties.find(
            'jp2HeaderBox/resolutionBox/captureResolutionBox')
        if resolutionBox is not None:
            numX = int(
                float(
                    resolutionBox.find('hRescInPixelsPerMeter').text) *
                100)
            numY = int(
                float(
                    resolutionBox.find('vRescInPixelsPerMeter').text) *
                100)
        else:
            # Then try the displayResolutionBox
            resolutionBox = properties.find(
                'jp2HeaderBox/resolutionBox/displayResolutionBox')
            if resolutionBox is not None:
                numX = int(
                    float(
                        resolutionBox.find('hResdInPixelsPerMeter').text) *
                    100)
                numY = int(
                    float(
                        resolutionBox.find('vResdInPixelsPerMeter').text) *
                    100)
        if resolutionBox is not None:
            mixSm = ET.Element('mix:SpatialMetrics')
            if self.mixFlag == 1:
                # always in S.I.
                mixSm.appendChildTagWithText('mix:samplingFrequencyUnit', '3')
            else:
                # always in S.I.
                mixSm.appendChildTagWithText('mix:samplingFrequencyUnit', 'cm')
            mixXSamplingFrequency = ET.Element('mix:xSamplingFrequency')
            mixXSamplingFrequency.appendChildTagWithText(
                'mix:numerator', str(numX))
            mixXSamplingFrequency.appendChildTagWithText(
                'mix:denominator', '10000')
            mixSm.append(mixXSamplingFrequency)
            mixYSamplingFrequency = ET.Element('mix:ySamplingFrequency')
            mixYSamplingFrequency.appendChildTagWithText(
                'mix:numerator', str(numY))
            mixYSamplingFrequency.appendChildTagWithText(
                'mix:denominator', '10000')
            mixSm.append(mixYSamplingFrequency)
            mixIam.append(mixSm)

        size = properties.find('contiguousCodestreamBox/siz')
        values = size.findall('ssizDepth')
        mixICE = ET.Element('mix:ImageColorEncoding')
        if self.mixFlag == 1:
            mixBPS = ET.Element('mix:bitsPerSample')
            mixICE.append(mixBPS)
            mixBPS.appendChildTagWithText('mix:bitsPerSampleValue',
                                          ','.join(map(lambda e: e.text, values)))
            mixBPS.appendChildTagWithText('mix:bitsPerSampleUnit', 'integer')
        else:
            mixBPS = ET.Element('mix:BitsPerSample')
            mixICE.append(mixBPS)
            for e in values:
                mixBPS.appendChildTagWithText('mix:bitsPerSampleValue', e.text)
            mixBPS.appendChildTagWithText('mix:bitsPerSampleUnit', 'integer')

        num = size.find('csiz').text
        mixICE.appendChildTagWithText('mix:samplesPerPixel', num)
        mixIam.append(mixICE)

        return mixIam

    def generateMix(self, properties):
        """Generate a mix representation."""
        xsiNsString = 'http://www.w3.org/2001/XMLSchema-instance'
        if self.mixFlag == 1:
            nsString = 'http://www.loc.gov/mix/v10'
            locSchemaString = ('http://www.loc.gov/mix/v10 '
                               'http://www.loc.gov/standards/mix/mix10/mix10.xsd')
        else:
            nsString = 'http://www.loc.gov/mix/v20'
            locSchemaString = ('http://www.loc.gov/mix/v20 '
                               'http://www.loc.gov/standards/mix/mix.xsd')

        mixRoot = ET.Element(
            'mix:mix', {'xmlns:mix': nsString,
                        'xmlns:xsi': xsiNsString,
                        'xsi:schemaLocation': locSchemaString})

        mixBdoi = self.generateMixBasicDigitalObjectInformation(properties)
        mixRoot.append(mixBdoi)
        mixBio = self.generateMixBasicImageInformation(properties)
        mixRoot.append(mixBio)
        mixIcm = self.generateMixImageCaptureMetadata(properties)
        if mixIcm and mixIcm is not None:
            mixRoot.append(mixIcm)
        mixIam = self.generateMixImageAssessmentMetadata(properties)
        mixRoot.append(mixIam)

        return mixRoot
