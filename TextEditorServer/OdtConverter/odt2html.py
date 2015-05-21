#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# $URL: svn://tengen/scripts/trunk/scripts/odt2html/odt2html.py $
#
# odt2html.py: Basic .odt to .html command line converter
# Copyright 2006 Ars Aperta http://arsaperta.com/
# Author: Jérôme Dumonteil <jerome.dumonteil@arsaperta.com>
# Included XSL file from Daniel Carrera taken from its odfreader perl 
# script.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""
    odt2html.py is a python command line script that makes a basic conversion 
    of a .odt (OpenDocument) text into a HTML file. Other conversions are 
    possible by changing the loaded XSL style sheet.

    By default, the result is sent to the standard output.

    -x filename.xsl , --xsl filename.xsl
    Specifies an alternate XSL sheet to be used for the conversion. Default 
    is to use the internal XSL data. 

    -o filename.xyz, --output filename.xyz
    Specifies a file in which to write the output. The default is the 
    standard output. 

    -a, --auto
    Build the output file name from the input file, by removing the .odt 
    suffix (if any) and adding the .html suffix. Usefull when several input 
    files are provided.    

    Although this XSL conversion would need more work around to obtain
    good quality ODF=>HTML conversion, here a small python version of
    the odf2html XSLT converter from the OpenDocument Fellowship.
    This version mimics the original functionalites, except it doesn't write 
    temp files on disk, uses standard python libs and thus may have some 
    portability. 
    -a option permits to convert several files at once, like '*.odt'
    -x option permits to load another XSL style file (default is to
    use embedded original one)
    
    You can find original perl script there :
    http://trac.opendocumentfellowship.org/odf2html/wiki/odfreader
    
    This script (and potentially newer versions) can be found there:
    http://arsaperta.org/odftoolsen.html/
    
"""

__version__="$Id: odt2html.py 2934 2006-07-31 13:13:25Z  $"

import os
import sys
import re
import optparse
import zipfile

import libxml2
import libxslt

VERSION="1.1"

# this XSL content is taken from "complete.xsl" of the odfreader-0.1 package :

quick_xsl="""<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:smil="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:int="http://opendocumentfellowship.org/internal" xmlns="http://www.w3.org/1999/xhtml" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" exclude-result-prefixes="office meta config text table draw presentation   dr3d chart form script style number anim dc xlink math xforms fo   svg smil ooo ooow oooc int #default">
  <xsl:variable name="lineBreak">
    <xsl:text>
</xsl:text>
  </xsl:variable>
  <xsl:template match="/office:document">
 <html>
  <head>
   <xsl:apply-templates select="office:document-meta"/>
  </head>
  <xsl:apply-templates select="office:document-content"/>
 </html>
</xsl:template>
  <xsl:template match="office:document-content">
 <body>
  <xsl:apply-templates select="office:body/office:text"/>
  <xsl:call-template name="add-footnote-bodies"/>
 </body>
</xsl:template>
  <xsl:template match="text:p">
 <p>
  <xsl:apply-templates/>
  <xsl:if test="count(node())=0"><br/></xsl:if>
 </p>
</xsl:template>
  <xsl:template match="text:span">
 <span>
  <xsl:apply-templates/>
 </span>
</xsl:template>
  <xsl:template match="text:h">
  <!-- Heading levels go only to 6 in XHTML -->
  <xsl:variable name="level">
    <xsl:choose>
      <!-- text:outline-level is optional, default is 1 -->
      <xsl:when test="not(@text:outline-level)">1</xsl:when>
      <xsl:when test="@text:outline-level &gt; 6">6</xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@text:outline-level"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:element name="{concat('h', $level)}">
    <a name="{generate-id()}"/>
    <xsl:apply-templates/>
  </xsl:element>
</xsl:template>
  <xsl:template match="text:tab">
 <xsl:text xml:space="preserve"> </xsl:text>
</xsl:template>
  <xsl:template match="text:line-break">
 <br/>
</xsl:template>
  <xsl:variable name="spaces" xml:space="preserve"/>
  <xsl:template match="text:s">
<xsl:choose>
 <xsl:when test="@text:c">
  <xsl:call-template name="insert-spaces">
   <xsl:with-param name="n" select="@text:c"/>
  </xsl:call-template>
 </xsl:when>
 <xsl:otherwise>
  <xsl:text> </xsl:text>
 </xsl:otherwise>
</xsl:choose>
</xsl:template>
  <xsl:template name="insert-spaces">
<xsl:param name="n"/>
<xsl:choose>
 <xsl:when test="$n &lt;= 30">
  <xsl:value-of select="substring($spaces, 1, $n)"/>
 </xsl:when>
 
 <xsl:otherwise>
  <xsl:value-of select="$spaces"/>
  <xsl:call-template name="insert-spaces">
   <xsl:with-param name="n">
    <xsl:value-of select="$n - 30"/>
   </xsl:with-param>
  </xsl:call-template>
 </xsl:otherwise>
</xsl:choose>
</xsl:template>
  <xsl:template match="text:a">
  <a href="{@xlink:href}"><xsl:apply-templates/></a>
</xsl:template>
  <xsl:template match="text:bookmark-start|text:bookmark">
 <a name="{@text:name}">
  <span style="font-size: 0px">
   <xsl:text> </xsl:text>
  </span>
 </a>
</xsl:template>
  <xsl:template match="text:note">
	<xsl:variable name="footnote-id" select="text:note-citation"/>
	<a href="#footnote-{$footnote-id}">
		<sup><xsl:value-of select="$footnote-id"/></sup>
	</a>
</xsl:template>
  <xsl:template match="text:note-body"/>
  <xsl:template name="add-footnote-bodies">
	<xsl:apply-templates select="//text:note" mode="add-footnote-bodies"/>
</xsl:template>
  <xsl:template match="text:note" mode="add-footnote-bodies">
	<xsl:variable name="footnote-id" select="text:note-citation"/>
	<p><a name="footnote-{$footnote-id}"><sup><xsl:value-of select="$footnote-id"/></sup>:</a></p>
	<xsl:apply-templates select="text:note-body/*"/>
</xsl:template>

  <xsl:template match="table:table">
 <table>
  <colgroup>
   <xsl:apply-templates select="table:table-column"/>
  </colgroup>
  <xsl:if test="table:table-header-rows/table:table-row">
   <thead>
   <xsl:apply-templates select="table:table-header-rows/table:table-row"/>
 </thead>
  </xsl:if>
  <tbody>
  <xsl:apply-templates select="table:table-row"/>
  </tbody>
 </table>
</xsl:template>
  <xsl:template match="table:table-column">
<col>
 <xsl:if test="@table:number-columns-repeated">
  <xsl:attribute name="span">
   <xsl:value-of select="@table:number-columns-repeated"/>
  </xsl:attribute>
 </xsl:if>
</col>
</xsl:template>
  <xsl:template match="table:table-row">
<tr>
 <xsl:apply-templates select="table:table-cell"/>
</tr>
</xsl:template>
  <xsl:template match="table:table-cell">
 <xsl:variable name="n">
  <xsl:choose>
   <xsl:when test="@table:number-columns-repeated != 0">
 <xsl:value-of select="@table:number-columns-repeated"/>
   </xsl:when>
   <xsl:otherwise>1</xsl:otherwise>
  </xsl:choose>
 </xsl:variable>
 <xsl:call-template name="process-table-cell">
  <xsl:with-param name="n" select="$n"/>
 </xsl:call-template>
</xsl:template>
  <xsl:template name="process-table-cell">
 <xsl:param name="n"/>
 <xsl:if test="$n != 0">
  <td>
  <xsl:if test="@table:number-columns-spanned">
   <xsl:attribute name="colspan">
 <xsl:value-of select="@table:number-columns-spanned"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:if test="@table:number-rows-spanned">
   <xsl:attribute name="rowspan">
 <xsl:value-of select="@table:number-rows-spanned"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:apply-templates/>
  </td>
  <xsl:call-template name="process-table-cell">
   <xsl:with-param name="n" select="$n - 1"/>
  </xsl:call-template>
 </xsl:if>
</xsl:template>
  <xsl:key name="listTypes" match="text:list-style" use="@style:name"/>
  <xsl:template match="text:list">
 <xsl:variable name="level" select="count(ancestor::text:list)+1"/>
 
 <!-- the list class is the @text:style-name of the outermost
  <text:list> element -->
 <xsl:variable name="listClass">
  <xsl:choose>
   <xsl:when test="$level=1">
 <xsl:value-of select="@text:style-name"/>
   </xsl:when>
   <xsl:otherwise>
 <xsl:value-of select="ancestor::text:list[last()]/@text:style-name"/>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:variable>
 
 <!-- Now select the <text:list-level-style-foo> element at this
  level of nesting for this list -->
 <xsl:variable name="node" select="key('listTypes',$listClass)/*[@text:level='$level']"/>

 <!-- emit appropriate list type -->
 <xsl:choose>
  <xsl:when test="local-name($node)='list-level-style-number'">
   <ol>
 <xsl:apply-templates/>
   </ol>
  </xsl:when>
  <xsl:otherwise>
   <ul>
 <xsl:apply-templates/>
   </ul>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>
  <xsl:template match="text:list-item">
 <li><xsl:apply-templates/></li>
</xsl:template>
  <xsl:template match="office:document-meta">
  <xsl:apply-templates/>
</xsl:template>
  <xsl:template match="office:meta">
  <xsl:comment> Metadata starts </xsl:comment>
  <xsl:apply-templates select="dc:title"/>
  <xsl:apply-templates select="dc:creator"/>
  <xsl:apply-templates select="dc:date"/>
  <xsl:apply-templates select="dc:language"/>
  <xsl:apply-templates select="dc:description"/>
  <xsl:apply-templates select="meta:keyword"/>
  <xsl:apply-templates select="meta:generator"/>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
  <xsl:comment> Metadata ends </xsl:comment>
</xsl:template>
  <xsl:template match="dc:title">
 <title><xsl:apply-templates/></title>
</xsl:template>
  <xsl:template match="dc:language">
 <meta http-equiv="content-language" content="{current()}"/>
</xsl:template>
  <xsl:template match="dc:creator">
 <meta name="author" content="{current()}"/>
 <meta name="DC.creator" content="{current()}"/>
</xsl:template>
  <xsl:template match="dc:description">
 <meta name="description" content="{current()}"/>
</xsl:template>
  <xsl:template match="dc:date">
 <meta name="revised" content="{current()}"/>
 <meta name="DC.date" content="{current()}"/>
</xsl:template>
  <xsl:template match="meta:keyword">
 <meta name="keywords" content="{current()}"/>
</xsl:template>
  <xsl:template match="meta:generator">
 <meta name="generator" content="{current()}"/>
</xsl:template>
  <xsl:param name="param_track_changes"/>
  <xsl:template match="text:tracked-changes">
  <xsl:comment> Document has track-changes on </xsl:comment>
</xsl:template>
  <xsl:template match="text:change">
 <xsl:if test="$param_track_changes">
   <xsl:variable name="id" select="@text:change-id"/>
   <xsl:variable name="change" select="//text:changed-region[@text:id=$id]"/>
   <xsl:element name="del">
     <xsl:attribute name="datetime">
       <xsl:value-of select="$change//dc:date"/>
     </xsl:attribute>
     <xsl:apply-templates match="$change/text:deletion/*"/>
   </xsl:element>
 </xsl:if>
</xsl:template>
  <xsl:template match="office:change-info"/>
  <xsl:param name="param_baseuri"/>
  <xsl:template match="draw:frame">
  <xsl:element name="div">
    <xsl:apply-templates/>
  </xsl:element>
</xsl:template>
  <xsl:template match="draw:frame/draw:image">
  <xsl:element name="img">
    <xsl:attribute name="alt">
      <xsl:value-of select="../svg:desc"/>
    </xsl:attribute>
    <xsl:attribute name="src">
      <xsl:value-of select="concat($param_baseuri,@xlink:href)"/>
    </xsl:attribute>
  </xsl:element>
</xsl:template>
  <xsl:template match="svg:desc"/>
  <xsl:template match="text:table-of-content">
  <!-- We don't parse the app's ToC but generate our own. -->
  <div>
    <xsl:apply-templates select="text:index-body/text:index-title"/>
    <xsl:apply-templates select="//text:h" mode="toc"/>
  </div>
</xsl:template>
  <xsl:template match="text:h" mode="toc">
  <xsl:element name="p">
    <a href="#{generate-id()}"><xsl:value-of select="."/></a>
  </xsl:element>
</xsl:template>
</xsl:stylesheet>

"""

class OdtOpener:
    """ manage read acces to internal components of the .odt file
    """
    re_xml=re.compile(r'^(<\?xml version=[^\n]*?\n)')
    base_items=('content.xml','meta.xml','styles.xml','settings.xml')
    
    def __init__(self,filepath):
        self.fp=os.path.abspath(os.path.expanduser(filepath))
        self.zip=zipfile.ZipFile(self.fp)
        for i in OdtOpener.base_items:
            self.open(i)
    
    def open(self,item):
        attribut=item.replace(".","_")   # no 'dot' in the attrib name :
                                         # beware hack, at first use, require
                                         # to open with the dotted name, 
                                         # except if already in base_items         
        if not hasattr(self,attribut):
            setattr(self, attribut, self.zip.read(item))
        return getattr(self,attribut)

    def mixed_content(self):
        mixed=[]
        mixed.append("<?xml version='1.0' encoding='UTF-8'?>\n")
        mixed.append("<office:document xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0'>\n")
        mixed.append( OdtOpener.re_xml.sub("",self.meta_xml))
        mixed.append( OdtOpener.re_xml.sub("",self.content_xml))
        mixed.append("</office:document>\n")
        return "".join(mixed)


class Xslizer:
    def __init__(self, xsl):
        """ xsl is the XSL content that will be applied by the XSLT processor
        """
        self.xsl=xsl
        sdoc = libxml2.parseDoc(self.xsl)
        self.style = libxslt.parseStylesheetDoc(sdoc)

    def apply(self, xml):
        """ xml is the xml style text
        """
        src=libxml2.parseDoc(xml)
        result = self.style.applyStylesheet(src, None)
        return self.style.saveResultToString(result)


class Odt2html:
    def __init__(self,xsl):
        """ Set up the convertissor with some xsl style
        """
        self.xslizer=Xslizer(xsl)
    
    def convert(self,file_path):
        """ read an odt file and send back the converted text
        """
        odt=OdtOpener(file_path)
        return self.xslizer.apply(odt.mixed_content())

def get_options():
    usage="usage: %prog [options] odt_file(s)"
    version="%prog  version "+VERSION
    parser = optparse.OptionParser(usage=usage,version=version)
    parser.add_option("-o", "--output", dest="outfile",
        help="save converted data to OUTPUT file")
    parser.add_option("-x", "--xsl", dest="xsl",
        help="load some alternate XSL converter")
    parser.add_option("-a", "--auto", dest="auto",action="store_true",
        default=False, help="name output files from input files")
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("need some odt files as argument")
    return (options, args)

def main(xsl_style=quick_xsl):
    suffix=".html"
    (options, args) = get_options()
    if options.xsl:         # read alternate XSL file
        xsl_style=file(options.xsl).read()
    C=Odt2html(xsl_style)   # load the XSL converter
    if options.auto:
        for odt_filename in args:
            if odt_filename.endswith(".odt"):
                output_filename=odt_filename[:-4]+suffix
            else:
                output_filename=odt_filename+suffix
            converted=C.convert(odt_filename)
            fh=file(output_filename,"w")
            fh.write(converted)
            fh.close()
    else:
        # only one .odt to convert
        if len(args)>1:
            print >> sys.stderr, "Warning, only converted the first argument file"
        odt_filename=args[0]
        
        converted=C.convert(odt_filename)
        
        if options.outfile:
            fh=file(options.outfile,"w")
            fh.write(converted)
            fh.close()
        else:
            # print result on standard output
            sys.stdout.write(converted)
            
if __name__=="__main__":
    main()

