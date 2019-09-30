"""Mix Property class to generate the mix property"""
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

from . import mix_constants as MIX

class Mix:
    """Class for generating NISO MIX image metadata
    """
    def __init__(self, mixFlag):
        self.mixFlag = mixFlag

    def generateMixBasicDigitalObjectInformation(self, properties):
        """Generate a mix BasicDigitalObjectInformation
        """
        mixBdoi = ET.Element(MIX.BASIC_DIGITAL_OB_INFO)

        mixFormatDesignation = ET.Element(MIX.FORMAT_DES)
        br = properties.find('fileTypeBox/br')
        if br is None:
            formatName = 'image/jp2'
        else:
            value = br.text
            formatName = 'image/' + value.strip()
        mixFormatDesignation.appendChildTagWithText(MIX.FORMAT_NAME, formatName)
        mixBdoi.append(mixFormatDesignation)
        if self.mixFlag == 1:
            mixBdoi.appendChildTagWithText(MIX.BYTE_ORDER, 'big_endian')
        else:
            mixBdoi.appendChildTagWithText(MIX.BYTE_ORDER, 'big endian')

        mixComp = ET.Element(MIX.COMPRESSION)
        compression = properties.find('contiguousCodestreamBox/cod/transformation').text
        if compression == '5-3 reversible':
            compressionScheme = 'JPEG 2000 Lossless'
        else:
            compressionScheme = 'JPEG 2000 Lossy'
        mixComp.appendChildTagWithText(MIX.COMPRESSION_SCHEME, compressionScheme)
        if self.mixFlag == 1:
            # compressionRatio is a int in mix 1...
            compressionRatio = int(round(float(properties.find('compressionRatio').text), 0))
            mixComp.appendChildTagWithText(MIX.COMPRESSION_RATIO, str(compressionRatio))
        else:
            # compressionRatio is a Rational in mix 2.0 (keep only 2 digits)
            value = int(round(float(properties.find('compressionRatio').text) * 100, 0))
            mixCompRatio = ET.Element(MIX.COMPRESSION_RATIO)
            mixCompRatio.appendChildTagWithText(MIX.NUMERATOR, str(value))
            mixCompRatio.appendChildTagWithText(MIX.DENOMINATOR, '100')
            mixComp.append(mixCompRatio)
        mixBdoi.append(mixComp)

        return mixBdoi

    def generateMixBasicImageInformation(self, properties):
        """Generate a mix BasicImageInformation
        """
        mixBio = ET.Element(MIX.BASIC_IMAGE_INFO)
        mixBic = ET.Element(MIX.BASIC_IMAGE_CHAR)
        width = str(properties.find('jp2HeaderBox/imageHeaderBox/width').text)
        height = str(properties.find('jp2HeaderBox/imageHeaderBox/height').text)
        mixBic.appendChildTagWithText(MIX.IMAGE_WIDTH, width)
        mixBic.appendChildTagWithText(MIX.IMAGE_HEIGHT, height)
        # Try ICC first
        iccElement = properties.find('jp2HeaderBox/colourSpecificationBox/icc')
        if iccElement:
            mixPI = ET.Element(MIX.PHOTOMETRIC_INT)
            colorSpace = properties.find('jp2HeaderBox/colourSpecificationBox/icc/colourSpace').text
            mixPI.appendChildTagWithText(MIX.COLOR_SPACE, colorSpace.strip())
            iccProfile = properties.find('jp2HeaderBox/colourSpecificationBox/icc/description').text
            mixColorProfile = ET.Element(MIX.COLOR_PROFILE)
            mixIccProfile = ET.Element(MIX.ICC_PROFILE)
            mixIccProfile.appendChildTagWithText(MIX.ICC_PROFILE_NAME, iccProfile)
            mixColorProfile.append(mixIccProfile)
            mixPI.append(mixColorProfile)
            mixBic.append(mixPI)
        else:
            mixPI = ET.Element(MIX.PHOTOMETRIC_INT)
            colorSpace = properties.find('jp2HeaderBox/colourSpecificationBox/enumCS').text
            mixPI.appendChildTagWithText(MIX.COLOR_SPACE, colorSpace.strip())
            mixBic.append(mixPI)
        mixBio.append(mixBic)

        mixSFC = ET.Element(MIX.SPECIAL_FORMAT_CHARS)
        mixJP2 = ET.Element(MIX.JPEG_2000)
        comment = properties.find('contiguousCodestreamBox/com/comment')
        if comment is not None:
            commentText = comment.text
            m = re.search(r'(.*)-v([0-9\.]*)', commentText)
            if m:
                # generate CodecCompliance only if it matches the regex
                mixCodecCompliance = ET.Element(MIX.CODEC_COMPLIANCE)
                mixCodecCompliance.appendChildTagWithText(MIX.CODEC, m.group(1))
                mixCodecCompliance.appendChildTagWithText(MIX.CODEC_VERSION, m.group(2))
                mixJP2.append(mixCodecCompliance)
        mixEncodingOptions = ET.Element(MIX.ENCODING_OPTIONS)
        tilesX = properties.find('contiguousCodestreamBox/siz/xTsiz').text
        tilesY = properties.find('contiguousCodestreamBox/siz/yTsiz').text
        if self.mixFlag == 1:
            tilesString = str(tilesX) + 'x' + str(tilesY)
            mixEncodingOptions.appendChildTagWithText(MIX.TILES, tilesString)
        else:
            mixTiles = ET.Element('mix:Tiles')
            mixTiles.appendChildTagWithText(MIX.TILE_WIDTH, str(tilesX))
            mixTiles.appendChildTagWithText(MIX.TILE_HEIGHT, str(tilesY))
            mixEncodingOptions.append(mixTiles)

        layers = properties.find('contiguousCodestreamBox/cod/layers').text
        if str(layers) != "0":
            mixEncodingOptions.appendChildTagWithText(MIX.QUALITY_LAYERS, str(layers))
        levels = properties.find('contiguousCodestreamBox/cod/levels').text
        if str(levels) != "0":
            mixEncodingOptions.appendChildTagWithText(MIX.RESOLUTION_LEVELS, str(levels))

        mixJP2.append(mixEncodingOptions)
        mixSFC.append(mixJP2)
        mixBio.append(mixSFC)
        return mixBio

    @staticmethod
    def findValueInRDF(prop, prefixPath, ns, tag):
        """Find a value in RDF : first as an element
        then as an attribute
        """
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
        """Look for a value in RDF and build a element, if found
        """
        value = Mix.findValueInRDF(prop, prefixPath, ns, tag)
        if value is not None:
            destEl.appendChildTagWithText(destTagName, value.strip())
            return True
        return False

    def generateMixImageCaptureMetadata(self, properties):
        """Generate a mix ImageCaptureMetadata
        """
        if self.mixFlag == 0:
            # Avoid a static method using self
            return None

        mixIcm = ET.Element(MIX.IMAGE_CAPTURE_MD)
        rdfBox = properties.find('xmlBox/{adobe:ns:meta/}xmpmeta/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
        if not rdfBox:
            rdfBox = properties.find('uuidBox/{adobe:ns:meta/}xmpmeta/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
        if not rdfBox:
            return None
        mixGci = ET.Element(MIX.GENERAL_CAPTURE_INFO)
        Mix.addIfExist(rdfBox,
                       '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                       '{http://ns.adobe.com/xap/1.0/}', 'CreateDate',
                       mixGci,
                       MIX.DATE_TIME_CREATED)
        Mix.addIfExist(rdfBox, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                       '{http://ns.adobe.com/tiff/1.0/}',
                       'Artist',
                       mixGci,
                       MIX.IMAGE_PRODUCER)
        mixIcm.append(mixGci)
        fillSc = False
        mixSc = ET.Element(MIX.SCANNER_CAPTURE)
        fillSc = Mix.addIfExist(rdfBox,
                                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                '{http://ns.adobe.com/tiff/1.0/}',
                                'Make',
                                mixSc,
                                MIX.SCANNER_MAN) or fillSc
        fillSm = False
        mixSm = ET.Element('mix:ScannerModel')
        fillSm = Mix.addIfExist(rdfBox,
                                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                '{http://ns.adobe.com/tiff/1.0/}',
                                'Model',
                                mixSm,
                                MIX.SCANNER_MODEL)
        fillSm = Mix.addIfExist(rdfBox,
                                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                '{http://ns.adobe.com/exif/1.0/aux/}',
                                'SerialNumber',
                                mixSm,
                                MIX.SCANNER_SERIAL_NO) or fillSm
        if fillSm:
            mixSc.append(mixSm)
            fillSc = True

        creatorTool = Mix.findValueInRDF(rdfBox,
                                         '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description',
                                         '{http://ns.adobe.com/xap/1.0/}',
                                         'CreatorTool')
        if creatorTool is not None:
            mixSss = ET.Element(MIX.SCANNING_SYS_SOFTWARE)
            m = re.search(r'^(.*) ([0-9\.]*)$', creatorTool)
            if m:
                mixSss.appendChildTagWithText(MIX.SCANNING_SOFTWARE_NAME, m.group(1))
                mixSss.appendChildTagWithText(MIX.SCANNING_SOFTWARE_VERSION, m.group(2))
            else:
                mixSss.appendChildTagWithText(MIX.SCANNING_SOFTWARE_NAME, creatorTool)
            mixSc.append(mixSss)
            fillSc = True

        if fillSc:
            mixIcm.append(mixSc)

        return mixIcm


    def generateMixImageAssessmentMetadata(self, properties):
        """Generate a mix ImageAssessmentMetadata
        """
        mixIam = ET.Element(MIX.IMAGE_ASSESMENT_MD)

        # Get the resolution in the captureResolutionBox first
        resolutionBox = properties.find('jp2HeaderBox/resolutionBox/captureResolutionBox')
        if resolutionBox is not None:
            numX = int(float(resolutionBox.find('hRescInPixelsPerMeter').text) * 100)
            numY = int(float(resolutionBox.find('vRescInPixelsPerMeter').text) * 100)
        else:
            # Then try the displayResolutionBox
            resolutionBox = properties.find('jp2HeaderBox/resolutionBox/displayResolutionBox')
            if resolutionBox is not None:
                numX = int(float(resolutionBox.find('hResdInPixelsPerMeter').text) * 100)
                numY = int(float(resolutionBox.find('vResdInPixelsPerMeter').text) * 100)
        if resolutionBox is not None:
            mixSm = ET.Element(MIX.SPATIAL_METRICS)
            if self.mixFlag == 1:
                mixSm.appendChildTagWithText(MIX.SAMPLING_FREQ_UNIT, '3') # always in S.I.
            else:
                mixSm.appendChildTagWithText(MIX.SAMPLING_FREQ_UNIT, 'cm') # always in S.I.
            mixXSamplingFrequency = ET.Element(MIX.X_SAMPLING_FREQUENCY)
            mixXSamplingFrequency.appendChildTagWithText(MIX.NUMERATOR, str(numX))
            mixXSamplingFrequency.appendChildTagWithText(MIX.DENOMINATOR, '10000')
            mixSm.append(mixXSamplingFrequency)
            mixYSamplingFrequency = ET.Element(MIX.Y_SAMPLING_FREQUENCY)
            mixYSamplingFrequency.appendChildTagWithText(MIX.NUMERATOR, str(numY))
            mixYSamplingFrequency.appendChildTagWithText(MIX.DENOMINATOR, '10000')
            mixSm.append(mixYSamplingFrequency)
            mixIam.append(mixSm)

        size = properties.find('contiguousCodestreamBox/siz')
        values = size.findall('ssizDepth')
        mixICE = ET.Element(MIX.IMAGE_COLOR_ENCODING)
        if self.mixFlag == 1:
            mixBPS = ET.Element(MIX.BITS_PER_SAMPLE)
            mixICE.append(mixBPS)
            mixBPS.appendChildTagWithText(MIX.BITS_PER_SAMPLE_VALUE,
                                          ','.join(map(lambda e: e.text, values)))
            mixBPS.appendChildTagWithText(MIX.BITS_PER_SAMPLE_UNIT, 'integer')
        else:
            mixBPS = ET.Element(MIX.BITS_PER_SAMPLE)
            mixICE.append(mixBPS)
            for e in values:
                mixBPS.appendChildTagWithText(MIX.BITS_PER_SAMPLE_VALUE, e.text)
            mixBPS.appendChildTagWithText(MIX.BITS_PER_SAMPLE_UNIT, 'integer')

        num = size.find('csiz').text
        mixICE.appendChildTagWithText(MIX.SAMPLES_PER_PIXEL, num)
        mixIam.append(mixICE)

        return mixIam

    def generateMix(self, properties):
        """Generate a mix representation
        """
        xsiNsString = 'http://www.w3.org/2001/XMLSchema-instance'
        if self.mixFlag == 1:
            nsString = 'http://www.loc.gov/mix/v10'
            locSchemaString = 'http://www.loc.gov/mix/v10 http://www.loc.gov/standards/mix/mix10/mix10.xsd'
        else:
            nsString = 'http://www.loc.gov/mix/v20'
            locSchemaString = 'http://www.loc.gov/mix/v20 http://www.loc.gov/standards/mix/mix.xsd'

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
