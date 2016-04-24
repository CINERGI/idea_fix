
import xml.etree.ElementTree as ET
from lxml import etree
import argparse
import logging
import os

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

def fixIedaFile(inFile, outfileName):
    if os.path.exists(outfileName):
        os.remove(outfileName)

    _nsmap = ET._namespace_map
    ET.register_namespace("http://www.isotc211.org/2005/gmd", "gmd")
    ET.register_namespace("http://www.isotc211.org/2005/gmi", "gmi")
    ET.register_namespace("http://www.isotc211.org/2005/gco", "gco")
    source = etree.parse(inFile).getroot()
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
    # fis keywords.
    # 1) place keyword not wrapped
    # 2) no place keyword
    for fixplace in source.findall('.//gmd:type/gmd:MD_KeywordTypeCode[@codeListValue="place"]/../../..',_nsmap):
        gmd_kw = etree.Element('{http://www.isotc211.org/2005/gmd}keyword')
        gmd_kw_cs = etree.Element('{http://www.isotc211.org/2005/gco}CharacterString')
        gmd_kw.insert(0,gmd_kw_cs)
        name = fixplace[0].text
        if name is not None and len(name) > 0:
            fixplace[0].text = None
            gmd_kw_cs.text= name
            gmd_mdkws = fixplace.find('gmd:MD_Keywords', _nsmap)
            gmd_mdkws.insert(0,gmd_kw)
        elif fixplace.find('{http://www.isotc211.org/2005/gmd}keyword'):
            logging.info('No place error in ' + inFile.name)
        else:
            fixplace.clear()  # remove it

# empty keyword
        for chkkw in source.findall('.//gmd:MD_Keywords',
                                       _nsmap):
            md_kw =  chkkw.find('{http://www.isotc211.org/2005/gmd}keyword', _nsmap)
            if md_kw is None:
                kw_type = chkkw.find('.//gmd:type/gmd:MD_KeywordTypeCode[@codeListValue]', _nsmap)
                logging.info(inFile.name + ": "+kw_type.text+' : empty keyword block removed')
                dist = chkkw.getparent()
                dist.getparent().remove(dist)    # remove it

    # < gmd:distributor >
    # < gmd:distributorContact >
   # / gmi:MI_Metadata / gmd:distributionInfo[1] / gmd:MD_Distribution[1] / gmd:distributor[1] / gmd:distributorContact[ 1]
    for fixdist in source.findall('.//gmd:distributor/gmd:distributorContact', _nsmap):
        parent = fixdist.getparent()
        md_dist = etree.Element('{http://www.isotc211.org/2005/gmd}MD_Distributor')
        md_dist.append(fixdist)
        parent.append(md_dist)

# missing distrubution info
    if  not source.findall('gmd:distributionInfo', _nsmap):
        logging.info(inFile.name + ': no distribution info. No file written')
        return None

#/gmi:MI_Metadata/gmd:identificationInfo[1]/gmd:MD_DataIdentification[1]/gmd:descriptiveKeywords[2]/gmd:MD_Keywords[1]/gmd:thesaurusName[1]/gmd:CI_Citation[1]
    for fixcitedate in source.findall('.//gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation', _nsmap):
        tag_date ='{http://www.isotc211.org/2005/gmd}date'
        gmd_date = etree.Element(tag_date)
        gmd_date.attrib['{http://www.isotc211.org/2005/gco}nilReason'] = 'unknown'
        if fixcitedate[0].tag == '{http://www.isotc211.org/2005/gmd}title' and fixcitedate[1].tag =='{http://www.isotc211.org/2005/gmd}identifier':
            fixcitedate.insert(1,gmd_date)

    et = etree.ElementTree(source)
    et.write(outfileName, pretty_print=True)

logging.basicConfig(filename='idea_fix.log',level=logging.INFO)

parser = argparse.ArgumentParser(description='Process some integers.')
#group = parser.add_mutually_exclusive_group(required=True)
filegroup = parser.add_argument_group('file')
filegroup.add_argument('--file',dest='isofile', type=argparse.FileType('r'),
                   help='single file')
# can't make it type=Filetype, or it get's created.
filegroup.add_argument('--outfile', dest='outfile',
                   help='output single file')
dirgroup = parser.add_argument_group('directory')
dirgroup.add_argument('--directory', dest='isodir',
                    help='directory of files')
dirgroup.add_argument('--output_directory', dest='outdir',
                      help='output directory of files')
args = parser.parse_args()

if args.isofile:
    fixIedaFile(args.isofile, args.outfile)
else:

    if os.path.exists(args.isodir) and os.path.isdir(args.isodir):
        if os.path.exists(args.outdir):
            if not os.path.isdir(args.outdir):
                Exception(args.outdir + " exists but is not a directory")
        else:
            os.makedirs(args.outdir)

        for root, dirs, files in os.walk(args.isodir):
            for file in files:
                if file.endswith(".xml"):
                    xmlfile = open(os.path.join(root, file))
                    outfile = os.path.join(args.outdir, file)
                    fixIedaFile(xmlfile, outfile)
