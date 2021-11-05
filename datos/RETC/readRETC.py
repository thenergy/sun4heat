#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 09:36:37 2021

@author: fcuevas
"""
import urllib
url = 'http://datosretc.mma.gob.cl/api/3/action/datastore_search?resource_id=ce629d88-c410-42e3-b170-de2afd89c395&limit=5&q=title:jones'  
fileobj = urllib.parse.urlparse(url)
print (fileobj.read())