# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 14:44:44 2014

@author: bokinsky
"""

import tempfile
# this import syntax only necessary for Python 2.x
# in Python 3.x, etree automatically imports cElementTree
#  by preference
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

mime = "application/vnd.oasis.opendocument.spreadsheet"
mani = """<?xml version='1.0' encoding='UTF-8'?>
<manifest:manifest>
 <manifest:file-entry
   manifest:media-type='application/vnd.oasis.opendocument.spreadsheet'
   manifest:full-path='/' />
 <manifest:file-entry
   manifest:media-type='text/xml'
   manifest:full-path='content.xml' />
</manifest:manifest>"""

def df_to_ods(df, path):
    mimetype = tempfile.TemporaryFile()
    mimetype.write(mime)
    
    manifest = tempfile.TemporaryFile()
    manifest.write(mani)