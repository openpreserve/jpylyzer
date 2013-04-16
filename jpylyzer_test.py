#!/usr/bin/env python

import doctest


def test_balloon_jp3():
    """
    >>> import jpylyzer
    >>> import os
    >>> jpylyzer.checkFiles([os.path.join('example_files','balloon.jp2'), ], pretty = True, test=True)
    <?xml version='1.0' encoding='ascii'?>
    <jpylyzer xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="adobe:ns:meta/" xmlns:ns3="http://ns.adobe.com/exif/1.0/" xmlns:ns4="http://ns.adobe.com/photoshop/1.0/" xmlns:ns5="http://ns.adobe.com/tiff/1.0/" xmlns:ns6="http://ns.adobe.com/xap/1.0/" xmlns:ns7="http://ns.adobe.com/xap/1.0/mm/" xmlns:ns8="http://ns.adobe.com/xap/1.0/sType/ResourceRef#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><toolInfo><toolName>jpylyzer_test.py</toolName><toolVersion>1.8.2</toolVersion></toolInfo><fileInfo><fileName>balloon.jp2</fileName><filePath>/home/aloha/jpylyzer/example_files/balloon.jp2</filePath><fileSizeInBytes>670265</fileSizeInBytes><fileLastModified>Fri Apr 12 19:28:14 2013</fileLastModified></fileInfo><isValidJP2>True</isValidJP2><tests /><properties><signatureBox /><fileTypeBox><br>jp2 </br><minV>0</minV><cL>jp2 </cL></fileTypeBox><jp2HeaderBox><imageHeaderBox><height>3701</height><width>2717</width><nC>3</nC><bPCSign>unsigned</bPCSign><bPCDepth>8</bPCDepth><c>jpeg2000</c><unkC>yes</unkC><iPR>no</iPR></imageHeaderBox><colourSpecificationBox><meth>Enumerated</meth><prec>0</prec><approx>0</approx><enumCS>sRGB</enumCS></colourSpecificationBox></jp2HeaderBox><uuidInfoBox><uuidListBox><nU>2</nU><uuid>6a706a70-6a70-6a70-6a70-6a706a706a70</uuid><uuid>61626162-6162-6162-6162-616261626162</uuid></uuidListBox><urlBox><version>0</version><loc>http://www.openplanetsfoundation.org/</loc></urlBox></uuidInfoBox><xmlBox><ns0:xmpmeta ns0:xmptk="Image::ExifTool 8.29"><rdf:RDF><rdf:Description rdf:about=""><dc:format>image/jpeg</dc:format>
     </rdf:Description>
    <BLANKLINE>
     <rdf:Description rdf:about=""><ns3:ColorSpace>65535</ns3:ColorSpace>
      <ns3:NativeDigest>256,257,258,259,262,274,277,284,530,531,282,283,296,301,318,319,529,532,306,270,271,272,305,315,33432;7EF15F60B74B2599BAEDB6749C30991A</ns3:NativeDigest>
      <ns3:PixelXDimension>2717</ns3:PixelXDimension>
      <ns3:PixelYDimension>3701</ns3:PixelYDimension>
     </rdf:Description>
    <BLANKLINE>
     <rdf:Description rdf:about=""><ns4:ColorMode>3</ns4:ColorMode>
      <ns4:History />
     </rdf:Description>
    <BLANKLINE>
     <rdf:Description rdf:about=""><ns5:BitsPerSample><rdf:Seq><rdf:li>8</rdf:li>
       </rdf:Seq>
      </ns5:BitsPerSample>
      <ns5:Compression>1</ns5:Compression>
      <ns5:ImageLength>3701</ns5:ImageLength>
      <ns5:ImageWidth>2717</ns5:ImageWidth>
      <ns5:NativeDigest>256,257,258,259,262,274,277,284,530,531,282,283,296,301,318,319,529,532,306,270,271,272,305,315,33432;7EF15F60B74B2599BAEDB6749C30991A</ns5:NativeDigest>
      <ns5:Orientation>1</ns5:Orientation>
      <ns5:PhotometricInterpretation>2</ns5:PhotometricInterpretation>
      <ns5:PlanarConfiguration>1</ns5:PlanarConfiguration>
      <ns5:ResolutionUnit>2</ns5:ResolutionUnit>
      <ns5:SamplesPerPixel>4</ns5:SamplesPerPixel>
      <ns5:Software>Adobe Photoshop CS3 Windows</ns5:Software>
      <ns5:XResolution>72/1</ns5:XResolution>
      <ns5:YCbCrSubSampling>1 1</ns5:YCbCrSubSampling>
      <ns5:YResolution>72/1</ns5:YResolution>
     </rdf:Description>
    <BLANKLINE>
     <rdf:Description rdf:about=""><ns6:CreateDate>2008-07-19T16:14:14-07:00</ns6:CreateDate>
      <ns6:CreatorTool>Adobe Photoshop CS3 Windows</ns6:CreatorTool>
      <ns6:MetadataDate>2008-07-19T16:14:14-07:00</ns6:MetadataDate>
      <ns6:ModifyDate>2008-07-19T16:14:14</ns6:ModifyDate>
     </rdf:Description>
    <BLANKLINE>
     <rdf:Description rdf:about=""><ns7:DerivedFrom rdf:parseType="Resource"><ns8:instanceID>uuid:AC48AD726754DD11BA6DEACED58C77FA</ns8:instanceID>
      </ns7:DerivedFrom>
      <ns7:DocumentID>uuid:6200E56DE155DD118C3CED023B237FE5</ns7:DocumentID>
      <ns7:InstanceID>uuid:6300E56DE155DD118C3CED023B237FE5</ns7:InstanceID>
     </rdf:Description>
    </rdf:RDF>
    </ns0:xmpmeta></xmlBox><contiguousCodestreamBox><siz><lsiz>47</lsiz><rsiz>ISO/IEC 15444-1</rsiz><xsiz>2717</xsiz><ysiz>3701</ysiz><xOsiz>0</xOsiz><yOsiz>0</yOsiz><xTsiz>1024</xTsiz><yTsiz>1024</yTsiz><xTOsiz>0</xTOsiz><yTOsiz>0</yTOsiz><numberOfTiles>12</numberOfTiles><csiz>3</csiz><ssizSign>unsigned</ssizSign><ssizDepth>8</ssizDepth><xRsiz>1</xRsiz><yRsiz>1</yRsiz><ssizSign>unsigned</ssizSign><ssizDepth>8</ssizDepth><xRsiz>1</xRsiz><yRsiz>1</yRsiz><ssizSign>unsigned</ssizSign><ssizDepth>8</ssizDepth><xRsiz>1</xRsiz><yRsiz>1</yRsiz></siz><cod><lcod>18</lcod><precincts>yes</precincts><sop>yes</sop><eph>yes</eph><order>RPCL</order><layers>6</layers><multipleComponentTransformation>yes</multipleComponentTransformation><levels>5</levels><codeBlockWidth>64</codeBlockWidth><codeBlockHeight>64</codeBlockHeight><codingBypass>no</codingBypass><resetOnBoundaries>no</resetOnBoundaries><termOnEachPass>no</termOnEachPass><vertCausalContext>no</vertCausalContext><predTermination>no</predTermination><segmentationSymbols>yes</segmentationSymbols><transformation>9-7 irreversible</transformation><precinctSizeX>128</precinctSizeX><precinctSizeY>128</precinctSizeY><precinctSizeX>128</precinctSizeX><precinctSizeY>128</precinctSizeY><precinctSizeX>128</precinctSizeX><precinctSizeY>128</precinctSizeY><precinctSizeX>128</precinctSizeX><precinctSizeY>128</precinctSizeY><precinctSizeX>256</precinctSizeX><precinctSizeY>256</precinctSizeY><precinctSizeX>256</precinctSizeX><precinctSizeY>256</precinctSizeY></cod><qcd><lqcd>35</lqcd><qStyle>scalar expounded</qStyle><guardBits>2</guardBits><mu>1816</mu><epsilon>13</epsilon><mu>1770</mu><epsilon>13</epsilon><mu>1770</mu><epsilon>13</epsilon><mu>1724</mu><epsilon>13</epsilon><mu>1792</mu><epsilon>12</epsilon></qcd><com><lcom>17</lcom><rcom>ISO/IEC 8859-15 (Latin)</rcom><comment>Jpylyzer demo</comment></com><tileParts><tilePart><sot><lsot>10</lsot><isot>0</isot><psot>67161</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>1</isot><psot>99064</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>2</isot><psot>36130</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>3</isot><psot>56048</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>4</isot><psot>140022</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>5</isot><psot>24008</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>6</isot><psot>46691</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>7</isot><psot>62671</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>8</isot><psot>26306</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>9</isot><psot>45614</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>10</isot><psot>38428</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart><tilePart><sot><lsot>10</lsot><isot>11</isot><psot>25064</psot><tpsot>0</tpsot><tnsot>1</tnsot></sot></tilePart></tileParts></contiguousCodestreamBox><compressionRatio>45.01</compressionRatio></properties></jpylyzer>
    """

if __name__ == '__main__':
    doctest.testmod()

