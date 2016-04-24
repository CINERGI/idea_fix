
import xml.etree.ElementTree as ET
from lxml import etree
import argparse

# <gmi:MI_Metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#  xmlns:xlink="http://www.w3.org/1999/xlink"
# xmlns:gco="http://www.isotc211.org/2005/gco"
#  xmlns:gmd="http://www.isotc211.org/2005/gmd"
# xmlns:gmx="http://www.isotc211.org/2005/gmx"
# xmlns:gml="http://www.opengis.net/gml/3.2"
#  xmlns:gss="http://www.isotc211.org/2005/gss"
# xmlns:gts="http://www.isotc211.org/2005/gts"
#  xmlns:gsr="http://www.isotc211.org/2005/gsr"
#  xmlns:gmi="http://www.isotc211.org/2005/gmi"
# xmlns:srv="http://www.isotc211.org/2005/srv"
# xmlns="http://www.isotc211.org/2005/gmi"
#  xsi:schemaLocation="http://www.isotc211.org/2005/gmi http://ngdc.noaa.gov/metadata/published/xsd/schema.xsd">

def fixIedaFile(filename):
    _nsmap = ET._namespace_map
    ET.register_namespace("http://www.isotc211.org/2005/gmd", "gmd")
    ET.register_namespace("http://www.isotc211.org/2005/gmi", "gmi")
    ET.register_namespace("http://www.isotc211.org/2005/gco", "gco")
    source = etree.parse(filename).getroot()
    #source.nsmap['gmi'] = source.nsmap[None] # gmi exists, so just remove none
    source.nsmap.pop(None)
    _nsmap = source.nsmap
    _nsmap.pop(None)
    for c in source.findall('.//gco:characterString',_nsmap):
        c.tag = "{http://www.isotc211.org/2005/gco}CharacterString"

#     < gmd:descriptiveKeywords >
#     < gmd:MD_Keywords > Antarctic
#     Peninsula
#     Peninsula < gmd:type >
#     < gmd:MD_KeywordTypeCode
#     codeListValue = "place"
#     codeList = "http://www.ngdc.noaa.gov/metadata/published/xsd/schema/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode" > place < / gmd:MD_KeywordTypeCode > < / gmd:type > < / gmd:MD_Keywords >
#
# < / gmd:descriptiveKeywords >
    for fixplace in source.findall('.//gmd:type/gmd:MD_KeywordTypeCode[@codeListValue="place"]/../../..',_nsmap):
        gmd_kw = etree.Element('{http://www.isotc211.org/2005/gmd}keyword')
        gmd_kw_cs = etree.Element('{http://www.isotc211.org/2005/gco}CharacterString')
        gmd_kw.insert(0,gmd_kw_cs)
        name = fixplace[0].text
        fixplace[0].text = None
        gmd_kw_cs.text= name
        gmd_mdkws = fixplace.find('gmd:MD_Keywords', _nsmap)
        gmd_mdkws.insert(0,gmd_kw)

    # < gmd:distributor >
    # < gmd:distributorContact >
   # / gmi:MI_Metadata / gmd:distributionInfo[1] / gmd:MD_Distribution[1] / gmd:distributor[1] / gmd:distributorContact[ 1]
    for fixdist in source.findall('.//gmd:distributor/gmd:distributorContact', _nsmap):
        parent = fixdist.getparent()
        md_dist = etree.Element('{http://www.isotc211.org/2005/gmd}MD_Distributor')
        md_dist.append(fixdist)
        parent.append(md_dist)

#/gmi:MI_Metadata/gmd:identificationInfo[1]/gmd:MD_DataIdentification[1]/gmd:descriptiveKeywords[2]/gmd:MD_Keywords[1]/gmd:thesaurusName[1]/gmd:CI_Citation[1]
    for fixcitedate in source.findall('.//gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation', _nsmap):
        gmd_date = etree.Element('{http://www.isotc211.org/2005/gmd}date')
        gmd_date.attrib['{http://www.isotc211.org/2005/gco}nilReason'] = 'unknown'
        fixcitedate.insert(1,gmd_date)

    et = etree.ElementTree(source)
    newFilename = filename.name
    newFilename = newFilename.replace('test_md','test_fixed')
    et.write(newFilename, pretty_print=True)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--file',dest='isofile', type=argparse.FileType('r'),
                   help='single file')
args = parser.parse_args()
fixIedaFile(args.isofile)