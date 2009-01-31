#===================================================================#
# Program: Easy Menu v. 1.0.3
# Short description: a multi-browser automagic extension builder
# Online resources: http://easymenu.googlepages.com/
#                   https://launchpad.net/easymenu
# File: files_generator.py
# Date: 2008/08/27
# Last modified: 2008/10/12
# Copyright (c) 2008 Riccardo Coccioli (Volans) <easymenu@gmail.com>
# License: GNU General Public License version 3
# Full license notice: ./LICENSE
#===================================================================#
# Easy Menu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Easy Menu is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# The copy of the GNU General Public License can be found here:
# ./lib/GPLv3License.txt
#
# You should have received a copy of the GNU General Public License
# along with Easy Menu. If not, see http://www.gnu.org/licenses/
#===================================================================#

"""Easy Menu v. 1.0.3
Automagically generate a Firefox and Flock extension that adds a Menu
with the structure given by a "well formatted" XML input.
See http://easymenu.googlepages.com/ for a full documentation.

Usage: python easymenu.py [OPTIONS] SOURCE

Where SOURCE can be:
- a path to a local XML file
- the URL of a remote XML file
- the special value "-" for standard input
- a string

Options list:
-t, --test             Test source input to check if it is valid or not
-c, --compatibility    The max version that will be used for the target
                       application compatibility. Possible values are:
                        - s => Standard (Firefox 3.0.* | Flock 1.2.*)
                        - p => Packaging (Firefox 3.1.* | Flock 1.2.*)
                        - t => Testing (Firefox 3.1.* | Flock 2.*)
-o, --overwrite        Overwrite without prompting all the output files
-s, --source           In addition to the .xpi file, generate also a
                       tar.gz compressed archive with the source code
-d, --debian           [EXPERIMENTAL] In addition to the .xpi file,
                       generate also the orig.tar.gz and diff.gz files
                       suitable for packaging purposes in Debian-based
                       systems.
-v, --version          Show version information and exit
-h, --help             Show this help information and exit
"""

import sys
import re
import codecs
from xml.etree import ElementTree as etree

from contents import *

def createTextElement(name, text, parent):
	"""
	Create a text node in the ElementTree XML API
	with given 'name', 'text' as content and
	attached as a child of 'parent' node.
	"""
	element = etree.SubElement(parent, name)
	element.text = text
	return element

def createSubElement(name, parent, attributes={}):
	"""
	Create a node in the  ElementTree XML API
	with the given 'name', attached as a child
	of 'parent' node and with given attributes,
	if any.
	"""
	element = etree.SubElement(parent, name, attributes)
	return element

def addDtdEntry(node, name):
	"""
	Add and entry in the DTD file corresponding to the locale
	specified in the 'locale' attribute of the 'node'.
	"""
	locale = node.attrib['locale']
	content = ''
	if node.text != None:
		content = node.text.replace('"', '&quot;').replace('&amp;', '&').replace('&', '&amp;')
	text = '<!ENTITY ' + c['internalName'] + '.' + name + ' "' + content + '">\n'
	if node.attrib.has_key('ak'):
		text += '<!ENTITY ' + c['internalName'] + '.' + name + '_ "' + node.attrib['ak'].replace('"', '&quot;').replace('&', '&amp;') + '">\n'
		ak = True
	else:
		ak = False

	try:
		file = codecs.open(c['locale'].replace('@@LOCALE_ID@@', locale) + '.dtd', 'a', 'utf-8')
		file.write(text)
		file.close()
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to update "' + locale + '" locale file\n -- EXIT --')
	return ak

def addUrlEntry(url):
	"""
	Add an entry in the 'url.properties' file
	"""
	text = c['internalName'] + '.url.' + str(c['tempId']) + '=' + url + '\n'
	try:
		file = codecs.open(c['dirName'] + '/chrome/content/' + c['internalName'] + '/url.properties', 'a', 'utf-8')
		file.write(text)
		file.close()
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to update "url.properties" file\n -- EXIT --')

def addStyles(node):
	"""
	Walk the styles of a given 'node' and set
	properties accordingly.
	"""
	classList = []
	for k, v in node.attrib.items():
		vv = v.lower()
		if k == 'bold':
			if vv == 'true':
				classList.append(c['internalName'] + '-b')
			else:
				sys.exit(' ERROR - Invalid bold attribute\n -- EXIT --')
		elif k == 'color':
			classList.append(c['internalName'] + '-c-' + vv)
			if vv not in c['colors']:
				c['colors'].append(vv)
		elif k == 'bg_col':
			classList.append(c['internalName'] + '-bg-' + vv)
			if vv not in c['bgColors']:
				c['bgColors'].append(vv)
	return classList

def addBgBoColors(node):
	"""
	Walk the background and border colors of a given 'node'
	and set properties accordingly.
	"""
	popClassList = []
	if node.attrib.has_key('border'):
		bo = node.attrib['border'].lower()
		popClassList.append(c['internalName'] + '-bo-' + bo)
		if bo not in c['boColors']:
			c['boColors'].append(bo)
	bg = node.text.lower()
	popClassList.append(c['internalName'] + '-bg-' + bg)
	if bg not in c['bgColors']:
		c['bgColors'].append(bg)
	return popClassList

def xulPreamble():
	"""
	Create the initial structure for XUL files
	in the ElementTree XML API.
	"""
	doc = etree.Element('overlay', {'xmlns':'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul'})
	createSubElement('script', doc, {'type':'application/x-javascript', 'src':'chrome://' + c['internalName'] + '/content/common.js'})
	createSubElement('script', doc, {'type':'application/x-javascript', 'src':'chrome://' + c['internalName'] + '/content/open.js'})
	stringbundleset = createSubElement('stringbundleset', doc, {'id':'stringbundleset'})
	createSubElement('stringbundle', stringbundleset, {'id':c['internalName'] + '-bundle', 'src':'chrome://' + c['internalName'] + '/content/url.properties'})
	return doc

def wrapText(text, width=70):
	"""
	A word-wrap function that preserves existing line breaks
	and most spaces in the text
	"""
	text = text.replace('\n\r', '\n')
	text = text.replace('\r', '\n')
	return reduce(lambda line, word, width=width: '%s%s%s' %
			(line, ' \n'[(len(line)-line.rfind('\n')-1 + len(word.split('\n',1)[0]) >= width)], word), text.split(' ')
		)

def insertMenuContent(nodeList, parent, w, i, firstPass):
	"""
	Walking a given ElementTree XML API node list
	call the relative function for each element.
	"""
	for node in nodeList:
		n = node.tag
		if n == 'menu':
			if firstPass:
				c['menu'].append(str(c['tempId']))
			insertMenu(node.getchildren(), parent, w, i)
		elif n == 'menuitem':
			insertMenuItem(node.getchildren(), parent, w, i)
		elif n == 'mailmenu':
			insertMailMenu(node, parent, w, i)
		elif n == 'searchitem':
			insertGetSearch(node.getchildren(), parent, w, i)
		elif n == 'customitem':
			insertCustomItem(node.getchildren(), parent, w, i)
		elif n == 'menuseparator':
			createSubElement('menuseparator', parent, {'id':c['internalName'] + '_' + i + '_' + str(c['tempId']), 'tooltiptext':''})
			c['tempId'] += 1

def insertMenu(nodeList, parent, w, i):
	"""
	Walk a given ElementTree XML API node list of
	childs of a 'menu' tag and set the properties
	needed to construct the XUL files accordingly.
	"""
	classList = ['menu-iconic']
	popClassList = []
	attributes = {'id':c['internalName'] + '_' + i + '_' + str(c['tempId']), 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + ';', 'onpopupshowing':c['internalName'] + 'Common.onMenuLoad(' + i + ');', 'tooltiptext':''}
	for node in nodeList:
		n = node.tag
		if n == 'bgcolor':
			popClassList.extend(addBgBoColors(node))
		elif n == 'style':
			classList.extend(addStyles(node))
		elif n == 'icon':
			classList.append(c['internalName'] + '-' + c['icons'][node.text])
		elif n == 'itemname':
			if w:
				if addDtdEntry(node, str(c['tempId'])):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
			else:
				if node.attrib.has_key('ak'):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
		elif n == 'tooltiptext':
			if w:
				addDtdEntry(node, str(c['tempId']) + '_t')
			if attributes['tooltiptext'] == '':
				attributes['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_t;'
		elif n == 'content':
			attributes['class'] = ' '.join(classList)
			menu = createSubElement('menu', parent, attributes)
			if popClassList:
				menupopup = createSubElement('menupopup', menu, {'class':' '.join(popClassList)})
			else:
				menupopup = createSubElement('menupopup', menu)
			c['tempId'] += 1
			insertMenuContent(node.getchildren(), menupopup, w, i, False)

def insertMenuItem(nodeList, parent, w, i):
	"""
	Walk a given ElementTree XML API node list of childs
	of a 'menuitem' tag and set the properties needed to
	construct the XUL files accordingly.
	"""
	classList = ['menuitem-iconic']
	attributes = {'id':c['internalName'] + '_' + i + '_' + str(c['tempId']), 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + ';', 'onclick':c['internalName'] + 'Url.openLink(event, "' + c['internalName'] + '.url.' + str(c['tempId']) + '");', 'oncommand':c['internalName'] + 'Url.openLink(null, "' + c['internalName'] + '.url.' + str(c['tempId']) + '");', 'tooltiptext':''}
	for node in nodeList:
		n = node.tag
		if n == 'style':
			classList.extend(addStyles(node))
		elif n == 'icon':
			classList.append(c['internalName'] + '-' + c['icons'][node.text])
		elif n == 'url' and w:
			addUrlEntry(node.text)
		elif n == 'itemname':
			if w:
				if addDtdEntry(node, str(c['tempId'])):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
			else:
				if node.attrib.has_key('ak'):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
		elif n == 'tooltiptext':
			if w:
				addDtdEntry(node, str(c['tempId']) + '_t')
			if attributes['tooltiptext'] == '':
				attributes['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_t;'
	attributes['class'] = ' '.join(classList)
	createSubElement('menuitem', parent, attributes)
	c['tempId'] += 1

def insertMailMenu(node, parent, w, i):
	"""
	Walk a given ElementTree XML API node list of childs
	of a 'mailmenu' tag and set the properties needed to
	construct the XUL files accordingly.
	"""
	classList = ['menu-iconic']
	popClassList = []
	attributes = {'id':c['internalName'] + '_' + i + '_' + str(c['tempId']), 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + ';', 'tooltiptext':''}
	mailAttr = {}
	mailOrders = ('thread', 'subject', 'author', 'date')
	icons = node.attrib['icons'].lower() == 'true'
	for node in node.getchildren():
		n = node.tag
		if n == 'bgcolor':
			popClassList.extend(addBgBoColors(node))
		elif n == 'style':
			classList.extend(addStyles(node))
		elif n == 'icon':
			classList.append(c['internalName'] + '-' + c['icons'][node.text])
		elif n == 'url' and w:
			c['mailMenu'][str(c['tempMailId'])] = node.text
		elif n == 'itemname':
			if w:
				if addDtdEntry(node, str(c['tempId'])):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
			else:
				if node.attrib.has_key('ak'):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
		elif n == 'tooltiptext':
			if w:
				addDtdEntry(node, str(c['tempId']) + '_t')
			if attributes['tooltiptext'] == '':
				attributes['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_t;'
		elif n == 'label':
			if w:
				addDtdEntry(node, str(c['tempId']) + 'l')
			if node.attrib.has_key('bold'):
				if node.attrib['bold'].lower() == 'true':
					mailAttr['label'] = True
		elif n in mailOrders:
			if w:
				if addDtdEntry(node, str(c['tempId']) + n[0]):
					mailAttr[n] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + n[0] + '_;'
			else:
				if node.attrib.has_key('ak'):
					mailAttr[n] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + n[0] + '_;'
	attributes['class'] = ' '.join(classList)
	menu = createSubElement('menu', parent, attributes)
	if popClassList:
		menupopup = createSubElement('menupopup', menu, {'class':' '.join(popClassList)})
	else:
		menupopup = createSubElement('menupopup', menu)
	labelClass = 'menuitem-iconic'
	if mailAttr.has_key('label'):
			labelClass += ' ' + c['internalName'] + '-b'
	createSubElement('menuitem', menupopup, {'class':labelClass, 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + 'l;', 'tooltiptext':''})
	for k in mailOrders:
		kClass = 'menuitem-iconic'
		if icons:
			kClass += ' ' + c['internalName'] + '-ml-' + k
		kAttr = {'class':kClass, 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + k[0] + ';', 'onclick':c['internalName'] + 'Common.mailArchive' + str(c['tempMailId']) + '(event, "' + k + '");', 'oncommand':c['internalName'] + 'Common.mailArchive' + str(c['tempMailId']) + '(null, "' + k + '");', 'tooltiptext':''}
		if mailAttr.has_key(k):
			kAttr['accesskey'] = mailAttr[k]
		createSubElement('menuitem', menupopup, kAttr)
	c['tempId'] += 1
	c['tempMailId'] += 1

def insertGetSearch(nodeList, parent, w, i):
	"""
	Walk a given ElementTree XML API node list of childs
	of a 'searchitem' tag and set the properties needed
	to construct the XUL files accordingly.
	"""
	classList = ['menuitem-iconic']
	attributes = {'id':c['internalName'] + '_' + i + '_' + str(c['tempId']), 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + ';', 'oncommand':c['internalName'] + 'Url.getSearchForm' + str(c['tempGetId']) + '(null, "@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + 'g;");', 'tooltiptext':''}
	for node in nodeList:
		n = node.tag
		if n == 'style':
			classList.extend(addStyles(node))
		elif n == 'icon':
			classList.append(c['internalName'] + '-' + c['icons'][node.text])
		elif n == 'url' and w:
			c['getForms'][str(c['tempGetId'])] = node.text
		elif n == 'itemname':
			if w:
				if addDtdEntry(node, str(c['tempId'])):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
			else:
				if node.attrib.has_key('ak'):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
		elif n == 'tooltiptext':
			if w:
				addDtdEntry(node, str(c['tempId']) + '_t')
			if attributes['tooltiptext'] == '':
				attributes['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_t;'
		elif n == 'searchlabel':
			if w:
				addDtdEntry(node,  str(c['tempId']) + 'g')
	attributes['class'] = ' '.join(classList)
	createSubElement('menuitem', parent, attributes)
	c['tempId'] += 1
	c['tempGetId'] += 1

def insertCustomItem(nodeList, parent, w, i):
	"""
	Walk a given ElementTree XML API node list of childs
	of a 'custoitem' tag and set the properties needed to
	construct the XUL files accordingly.
	"""
	classList = ['menuitem-iconic']
	attributes = {'id':c['internalName'] + '_' + i + '_c' + str(c['tempCustId']), 'label':'@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + ';', 'onclick':c['internalName'] + 'Common.customPage' + str(c['tempCustId']) + '(event);', 'oncommand':c['internalName'] + 'Common.customPage' + str(c['tempCustId']) + '(null);', 'tooltiptext':''}
	for node in nodeList:
		n = node.tag
		if n == 'style':
			classList.extend(addStyles(node))
		elif n == 'icon':
			classList.append(c['internalName'] + '-' + c['icons'][node.text])
		elif n == 'url' and w:
			c['customPages'].append((str(c['tempCustId']), node.text))
		elif n == 'itemname':
			if w:
				if addDtdEntry(node, str(c['tempId'])):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
			else:
				if node.attrib.has_key('ak'):
					attributes['accesskey'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_;'
		elif n == 'tooltiptext':
			if w:
				addDtdEntry(node, str(c['tempId']) + '_t')
			if attributes['tooltiptext'] == '':
				attributes['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.' + str(c['tempId']) + '_t;'
		elif n == 'customlabel':
			if w:
				addDtdEntry(node,  'CustomPage' + str(c['tempCustId']))
	attributes['class'] = ' '.join(classList)
	createSubElement('menuitem', parent, attributes)
	c['tempId'] += 1
	c['tempCustId'] += 1

def installRdf(extensionTag):
	"""
	Create the ElementTree XML API structure of the install.rdf file
	"""
	doc = etree.Element('RDF', {'xmlns:em':'http://www.mozilla.org/2004/em-rdf#', 'xmlns':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
	description = createSubElement('Description', doc, {'about':'urn:mozilla:install-manifest'})
	createTextElement('em:id', c['id'], description)
	createTextElement('em:name', c['name'], description)
	createTextElement('em:version', c['version'], description)
	createTextElement('em:creator', c['author'], description)
	createTextElement('em:homepageURL', c['homepageURL'], description)
	if c['logo']:
		createTextElement('em:iconURL', install['icon'], description)
	aboutURL = install['aboutURL'].replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
	createTextElement('em:aboutURL', aboutURL, description)
	optionsURL = install['optionsURL'].replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
	createTextElement('em:optionsURL', optionsURL, description)
	for locale in extensionTag.findall('localized'):
		localized = createSubElement('em:localized', description)
		localDesc = createSubElement('Description', localized)
		if locale.find('name') != None:
			name = locale.findtext('name')
		else:
			name = c['name']
		createTextElement('em:name', name, localDesc)
		createTextElement('em:version', c['version'], localDesc)
		createTextElement('em:creator', c['author'], localDesc)
		createTextElement('em:locale', locale.attrib['locale'], localDesc)
		createTextElement('em:homepageURL', c['homepageURL'], localDesc)
		createTextElement('em:description', c[locale.attrib['locale'] + 'Desc'], localDesc)
	createTextElement('em:description', extensionTag.findtext('en-description'), description)
	file = createSubElement('em:file', description)
	fileDesc = createSubElement('Description', file, {'about':'urn:mozilla:extension:file:' + c['internalName'] + '.jar'})
	createTextElement('em:package', 'content/' + c['internalName'] + '/', fileDesc)
	createTextElement('em:skin', 'skin/classic/' + c['internalName'] + '/', fileDesc)
	for fileLocale in c['locales'].keys():
		createTextElement('em:locale', 'locale/' + fileLocale + '/' + c['internalName'] + '/', fileDesc)
	target = createSubElement('em:targetApplication', description)
	target.append(etree.Comment('Firefox compatibility: from ' + c['ffoxMinVersion'] + ' to ' + c['ffoxMaxVersion'][c['compatibility']]))
	targetDesc = createSubElement('Description', target)
	createTextElement('em:id', '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}', targetDesc)
	createTextElement('em:minVersion', c['ffoxMinVersion'], targetDesc)
	createTextElement('em:maxVersion', c['ffoxMaxVersion'][c['compatibility']], targetDesc)
	target2 = createSubElement('em:targetApplication', description)
	target2.append(etree.Comment('Flock compatibility: from ' + c['flockMinVersion'] + ' to ' + c['flockMaxVersion'][c['compatibility']]))
	targetDesc2 = createSubElement('Description', target2)
	createTextElement('em:id', '{a463f10c-3994-11da-9945-000d60ca027b}', targetDesc2)
	createTextElement('em:minVersion', c['flockMinVersion'], targetDesc2)
	createTextElement('em:maxVersion', c['flockMaxVersion'][c['compatibility']], targetDesc2)
	return doc

def skinContentsRdf():
	"""
	Create the ElementTree XML API structure of
	the contents.rdf file in skin folder.
	"""
	doc = etree.Element('RDF:RDF', {'xmlns:chrome':'http://www.mozilla.org/rdf/chrome#', 'xmlns:RDF':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
	rdfSeq = createSubElement('RDF:Seq', doc, {'about':'urn:mozilla:skin:root'})
	createSubElement('RDF:li', rdfSeq, {'resource':'urn:mozilla:skin:classic/1.0'})
	rdfDescription = createSubElement('RDF:Description', doc, {'about':'urn:mozilla:skin:classic/1.0'})
	chromePackages = createSubElement('chrome:packages', rdfDescription)
	rdfSeq = createSubElement('RDF:Seq', chromePackages, {'about':'urn:mozilla:skin:classic/1.0:packages'})
	createSubElement('RDF:li', rdfSeq, {'resource':'urn:mozilla:skin:classic/1.0:' + c['internalName']})
	rdfSeq = createSubElement('RDF:Seq', doc, {'about':'urn:mozilla:stylesheets'})
	createSubElement('RDF:li', rdfSeq, {'resource':'chrome://browser/content/browser.xul'})
	createSubElement('RDF:li', rdfSeq, {'resource':'chrome://global/content/customizeToolbar.xul'})
	rdfSeq = createSubElement('RDF:Seq', doc, {'about':'chrome://browser/content/browser.xul'})
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/skin/' + c['internalName'] + '.css', rdfSeq)
	rdfSeq = createSubElement('RDF:Seq', doc, {'about':'chrome://global/content/customizeToolbar.xul'})
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/skin/' + c['internalName'] + '.css', rdfSeq)
	return doc

def localeContentsRdf(locale, localeName):
	"""
	Create the ElementTree XML API structure of
	the contents.rdf file in all locale folders.
	"""
	doc = etree.Element('RDF:RDF', {'xmlns:chrome':'http://www.mozilla.org/rdf/chrome#', 'xmlns:RDF':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
	rdfSeq = createSubElement('RDF:Seq', doc, {'about':'urn:mozilla:locale:root'})
	createSubElement('RDF:li', rdfSeq, {'resource':'urn:mozilla:locale:' + locale})
	rdfDescription = createSubElement('RDF:Description', doc, {'about':'urn:mozilla:locale:' + locale, 'chrome:displayName':localeName, 'chrome:author':c['author'], 'chrome:name':locale})
	chromePackages = createSubElement('chrome:packages', rdfDescription)
	rdfSeq = createSubElement('RDF:Seq', chromePackages, {'about':'urn:mozilla:locale:' + locale + ':packages'})
	createSubElement('RDF:li', rdfSeq, {'resource':'urn:mozilla:locale:' + locale + ':' + c['internalName']})
	return doc

def contentContentsRdf():
	"""
	Create the ElementTree XML API structure of
	the contents.rdf file in the contents folder.
	"""
	doc = etree.Element('RDF:RDF', {'xmlns:chrome':'http://www.mozilla.org/rdf/chrome#', 'xmlns:RDF':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})
	rdfSeq = createSubElement('RDF:Seq', doc, {'RDF:about':'urn:mozilla:package:root'})
	createSubElement('RDF:li', rdfSeq, {'RDF:resource':'urn:mozilla:package:' + c['internalName']})
	rdfSeq2 = createSubElement('RDF:Seq', doc, {'RDF:about':'urn:mozilla:overlays'})
	createSubElement('RDF:li', rdfSeq2, {'RDF:resource':'chrome://browser/content/browser.xul'})
	createSubElement('RDF:li', rdfSeq2, {'RDF:resource':'chrome://global/content/customizeToolbar.xul'})
	rdfSeq3 = createSubElement('RDF:Seq', doc, {'RDF:about':'chrome://browser/content/browser.xul'})
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/content/titleMenu.xul', rdfSeq3)
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/content/toolsMenu.xul', rdfSeq3)
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/content/contextMenu.xul', rdfSeq3)
	rdfSeq4 = createSubElement('RDF:Seq', doc, {'about':'chrome://global/content/customizeToolbar.xul'})
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/content/titleMenu.xul', rdfSeq4)
	rdfSeq5 = createSubElement('RDF:Seq', doc, {'about':'chrome://navigator/content/navigator.xul'})
	createTextElement('RDF:li', 'chrome://' + c['internalName'] + '/content/titleMenu.xul', rdfSeq5)
	authorUrl = c['authorUrl'] or 'mailto:' + c['authorEmail']
	attributes = {'RDF:about':'urn:mozilla:package:' + c['internalName'], 'chrome:displayName':c['name'], 'chrome:author':c['author'], 'chrome:authorURL':authorUrl, 'chrome:name':c['internalName'], 'chrome:extension':'true', 'chrome:settingsURL':'chrome://' + c['internalName'] + '/content/prefs.xul', 'chrome:description':c['oneLineDesc']}
	if c['logo']:
		attributes['chrome:iconURL'] = install['icon']
	createSubElement('RDF:Description', doc, attributes)
	return doc

def aboutXul():
	"""
	Create the ElementTree XML API structure of the about.xul file
	"""
	doc = etree.Element('dialog', {'xmlns':'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'id':c['internalName'] + 'About', 'title':'@@INTERNAL_ENTITY_NAME@@.MenuName;', 'maxwidth':'200', 'buttons':'accept'})
	script = createTextElement('script', aboutXulScript, doc)
	script.attrib = {'type':'application/x-javascript'}
	vbox1 = createSubElement('vbox', doc, {'flex':'1', 'align':'center'})
	hbox1 = createSubElement('hbox', vbox1, {'flex':'1'})
	if c['logo']:
		createSubElement('image', hbox1, {'src':install['icon']})
	createSubElement('label', hbox1, {'value':'@@INTERNAL_ENTITY_NAME@@.MenuName;', 'style':'font-weight:bold; font-size:x-large;'})
	createSubElement('separator', vbox1, {'class':'thin'})
	hbox2 = createSubElement('hbox', vbox1, {'flex':'1'})
	createSubElement('label', hbox2, {'value':'Changelog', 'align':'left', 'class':'text-link', 'onclick':'about_open("chrome://' + c['internalName'] + '/locale/CHANGELOG", "chrome,resizable=yes,centerscreen,scrollbars=auto,width=550,height=400")'})
	createSubElement('label', hbox2, {'value':'v. ' + c['version'] + ' - ' + c['datetime'][:10], 'align':'center'})
	createSubElement('label', hbox2, {'value':'License', 'align':'right', 'class':'text-link', 'onclick':'about_open("chrome://' + c['internalName'] + '/content/LICENSE", "chrome,resizable=yes,centerscreen,scrollbars=auto")'})
	createSubElement('separator', vbox1, {'class':'thin'})
	vbox2 = createSubElement('vbox', doc, {'flex':'1'})
	hbox3 = createSubElement('hbox', vbox2)
	createSubElement('label', hbox3, {'value':'Created by:', 'style':'font-weight: bold;'})
	authorUrl = c['authorUrl'] or 'mailto:' + c['authorEmail']
	createSubElement('label', hbox3, {'value':c['author'], 'href':authorUrl, 'class':'text-link'})
	hbox4 = createSubElement('hbox', vbox2)
	createSubElement('label', hbox4, {'value':'Homepage:', 'style':'font-weight: bold;'})
	createSubElement('label', hbox4, {'value':c['homepageURL'], 'href':c['homepageURL'], 'class':'text-link'})
	createSubElement('separator', vbox2, {'class':'thin'})
	createSubElement('label', vbox2, {'value':'Description:', 'style':'font-weight: bold;'})
	for descLine in c['description'].split('\n'):
		createSubElement('description', vbox2, {'value':descLine})
	createSubElement('separator', vbox2, {'class':'thin', 'style':'height:2em; border-bottom:1px dotted #000;'})
	createSubElement('separator', vbox2, {'class':'thin'})
	createSubElement('label', vbox2, {'value':'@@INTERNAL_ENTITY_NAME@@.MenuName; was automagically generated by: ', 'style':'font-size:small;'})
	hbox5 = createSubElement('hbox', vbox2)
	createSubElement('label', hbox5, {'value':'Easy Menu', 'href':c['emSite'], 'class':'text-link', 'style':'font-size:small;'})
	createSubElement('label', hbox5, {'value':'v.' + c['emVersion'] + ' on ' + c['datetime'] + ' UTC', 'style':'font-size:small; align:left;'})
	return doc

def prefsXul():
	"""
	Create the ElementTree XML API structure of the prefs.xul file
	"""
	doc = etree.Element('dialog', {'xmlns':'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'id':c['internalName'] + 'Options', 'title':'Options...', 'style':'width: 430px; height: 300px;', 'buttons':'accept,cancel', 'onload':c['internalName'] + 'Options.onDialogLoad();', 'ondialogaccept':c['internalName'] + 'Options.onDialogAccept();' + c['internalName'] + 'Common.onLoad();'})
	createSubElement('script', doc, {'type':'application/x-javascript', 'src':'chrome://' + c['internalName'] + '/content/common.js'})
	createSubElement('script', doc, {'type':'application/x-javascript', 'src':'chrome://' + c['internalName'] + '/content/prefs.js'})
	tabbox = createSubElement('tabbox', doc)
	tabs = createSubElement('tabs', tabbox)
	createSubElement('tab', tabs, {'label':'Appearance'})
	if c['menu']:
		createSubElement('tab', tabs, {'label':'Sub Menus'})
	if c['customPages']:
		createSubElement('tab', tabs, {'label':'Custom Pages'})
	tabpanels = createSubElement('tabpanels', tabbox)
	tabpanel = createSubElement('tabpanel', tabpanels)
	groupbox = createSubElement('groupbox', tabpanel, {'flex':'1'})
	createSubElement('caption', groupbox, {'label':'Where to show the main menu'})
	createSubElement('spacer', groupbox, {'flex':'1'})
	createSubElement('checkbox', groupbox, {'id':'TitleMenu', 'label':'In the main menu bar'})
	createSubElement('checkbox', groupbox, {'id':'ToolsMenu', 'label':'In the Tools menu'})
	createSubElement('checkbox', groupbox, {'id':'ContextMenu', 'label':'In the context menu'})
	if c['logo']:
		createSubElement('checkbox', groupbox, {'id':'ShowLogo', 'label':'Show logo in the main menus'})
	createSubElement('spacer', groupbox, {'flex':'1'})

	if c['menu']:
		tabpanel2 = createSubElement('tabpanel', tabpanels)
		groupbox2 = createSubElement('groupbox', tabpanel2, {'flex':'1'})
		createSubElement('caption', groupbox2, {'label':'Which menu insert'})
		createSubElement('spacer', groupbox2, {'flex':'1'})
		for menu in c['menu']:
			createSubElement('checkbox', groupbox2, {'id':'SubMenu' + menu, 'label':'@@INTERNAL_ENTITY_NAME@@.' + menu + ';'})
		createSubElement('checkbox', groupbox2, {'id':'Options', 'label':'Options...'})
		createSubElement('spacer', groupbox2, {'flex':'1'})

	if c['customPages']:
		tabpanel3 = createSubElement('tabpanel', tabpanels)
		groupbox3 = createSubElement('groupbox', tabpanel3, {'flex':'1'})
		createSubElement('caption', groupbox3, {'label':'Insert your custom pages name'})
		createSubElement('spacer', groupbox3, {'flex':'1'})
		for t in c['customPages']:
			createSubElement('label', groupbox3, {'control':'CustomPage' + t[0], 'value':'@@INTERNAL_ENTITY_NAME@@.CustomPage' + t[0] + ';', 'tooltiptext':t[1]})
			createSubElement('textbox', groupbox3, {'id':'CustomPage' + t[0]})
		createSubElement('spacer', groupbox3, {'flex':'1'})
	return doc

def createCss():
	"""
	Create the content of the css file in skin folder
	"""
	doc = c['cssjsPreamble']
	doc += '.' + c['internalName'] + '-b	{ font-weight: bold; }\n'
	doc += '.' + c['internalName'] + '-o	{ list-style-image: url("chrome://' + c['internalName'] + '/skin/icons/options.png"); }\n'
	if c['iconTitle']:
		doc += '.' + c['internalName'] + '-l	{ list-style-image: url("chrome://' + c['internalName'] + '/skin/icons/' + c['icons'][c['iconTitle']] + '.png") !important; }\n'
	if c['showMailIcons']:
		for icon in c['mailIcons']:
			doc += '.' + c['internalName'] + '-ml-' + icon + '	{ list-style-image: url("chrome://' + c['internalName'] + '/skin/icons/ml_' + icon + '.png"); }\n'
	for color in c['colors']:
		doc += '.' + c['internalName'] + '-c-' + color + '	{ color: #' + color + '; }\n'
	for color in c['bgColors']:
		doc += '.' + c['internalName'] + '-bg-' + color + '	{ -moz-appearance: none; background-color: #' + color + '; }\n'
	for color in c['boColors']:
		doc += '.' + c['internalName'] + '-bo-' + color + '	{ border: 1px solid #' + color + '; }\n'
	for v in c['icons'].values():
		doc += '.' + c['internalName'] + '-' + v + '	{ list-style-image: url("chrome://' + c['internalName'] + '/skin/icons/' + v + '.png"); }\n'
	return doc

def titleMenuXul(nodeList):
	"""
	Create the ElementTree XML API structure of the titleMenu.xul file
	"""
	doc = xulPreamble()
	menubar = createSubElement('menubar', doc, {'id':'main-menubar'})
	classList = ['menu-iconic']
	if c['iconTitle']:
		classList.append(c['internalName'] + '-l')
	attrList = {'id':c['internalName'] + 'TitleMenu', 'onpopupshowing':c['internalName'] + 'Common.onMenuLoad("1");', 'position':'8', 'label':'@@INTERNAL_ENTITY_NAME@@.MenuName;', 'accesskey':'@@INTERNAL_ENTITY_NAME@@.MenuName_;', 'class':' '.join(classList), 'tooltiptext':''}
	if c['tooltiptext']:
		attrList['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.MenuName_t;'
	menu = createSubElement('menu', menubar, attrList)
	attrList = {'id':c['internalName'] + 'TitleMenuPopup'}
	if c['bgColMenu']:
		if c['boColMenu']:
			attrList['class'] = c['internalName'] + '-bg-' + c['bgColMenu'] + ' ' + c['internalName'] + '-bo-' + c['boColMenu']
		else:
			attrList['class'] = c['internalName'] + '-bg-' + c['bgColMenu']
	menupopup = createSubElement('menupopup', menu, attrList)
	c['tempId'] = 1
	c['tempMailId'] = 1
	c['tempGetId'] = 1
	c['tempCustId'] = 1
	insertMenuContent(nodeList, menupopup, True, '1', True)
	createSubElement('menuseparator', menupopup, {'id':c['internalName'] + 'SepOptions1', 'tooltiptext':''})
	createSubElement('menuitem', menupopup, {'id':c['internalName'] + 'Options1', 'class':'menu-iconic ' + c['internalName'] + '-o', 'label':'Options...', 'tooltiptext':'', 'oncommand':'window.openDialog("chrome://' + c['internalName'] + '/content/prefs.xul","' + c['internalName'] + ' - Options","chrome,resizable=yes,centerscreen");'})
	return doc

def toolsMenuXul(nodeList):
	"""
	Create the ElementTree XML API structure of the toolsMenu.xul file
	"""
	doc = xulPreamble()
	menupopup = createSubElement('menupopup', doc, {'id':'menu_ToolsPopup'})
	classList = ['menu-iconic']
	if c['iconTitle']:
		classList.append(c['internalName'] + '-l')
	attrList = {'id':c['internalName'] + 'ToolsMenu', 'onpopupshowing':c['internalName'] + 'Common.onMenuLoad("2");', 'insertafter':'devToolsSeparator', 'label':'@@INTERNAL_ENTITY_NAME@@.MenuName;', 'accesskey':'@@INTERNAL_ENTITY_NAME@@.MenuName_;', 'class':' '.join(classList), 'tooltiptext':''}
	if c['tooltiptext']:
		attrList['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.MenuName_t;'
	menu = createSubElement('menu', menupopup, attrList)
	attrList = {'id':c['internalName'] + 'ToolsMenuPopup'}
	if c['bgColMenu']:
		if c['boColMenu']:
			attrList['class'] = c['internalName'] + '-bg-' + c['bgColMenu'] + ' ' + c['internalName'] + '-bo-' + c['boColMenu']
		else:
			attrList['class'] = c['internalName'] + '-bg-' + c['bgColMenu']
	menupopup2 = createSubElement('menupopup', menu, attrList)
	c['tempId'] = 1
	c['tempMailId'] = 1
	c['tempGetId'] = 1
	c['tempCustId'] = 1
	insertMenuContent(nodeList, menupopup2, False, '2', False)
	createSubElement('menuseparator', menupopup2, {'id':c['internalName'] + 'SepOptions2', 'tooltiptext':''})
	createSubElement('menuitem', menupopup2, {'id':c['internalName'] + 'Options2', 'class':'menu-iconic ' + c['internalName'] + '-o', 'label':'Options...', 'tooltiptext':'', 'oncommand':'window.openDialog("chrome://' + c['internalName'] + '/content/prefs.xul","' + c['internalName'] + ' - Options","chrome,resizable=yes,centerscreen");'})
	return doc

def contextMenuXul(nodeList):
	"""
	Create the ElementTree XML API structure of the contextMenu.xul file
	"""
	doc = xulPreamble()
	popup = createSubElement('popup', doc, {'id':'contentAreaContextMenu'})
	classList = ['menu-iconic']
	if c['iconTitle']:
		classList.append(c['internalName'] + '-l')
	attrList = {'id':c['internalName'] + 'ContextMenu', 'onpopupshowing':c['internalName'] + 'Common.onMenuLoad("3");', 'insertafter':'context-stop', 'label':'@@INTERNAL_ENTITY_NAME@@.MenuName;', 'accesskey':'@@INTERNAL_ENTITY_NAME@@.MenuName_;', 'class':' '.join(classList), 'tooltiptext':''}
	if c['tooltiptext']:
		attrList['tooltiptext'] = '@@INTERNAL_ENTITY_NAME@@.MenuName_t;'
	menu = createSubElement('menu', popup, attrList)
	attrList =  {'id':c['internalName'] + 'ContextMenuPopup'}
	if c['bgColMenu']:
		if c['boColMenu']:
			attrList['class'] = c['internalName'] + '-bg-' + c['bgColMenu'] + ' ' + c['internalName'] + '-bo-' + c['boColMenu']
		else:
			attrList['class'] = c['internalName'] + '-bg-' + c['bgColMenu']
	menupopup = createSubElement('menupopup', menu, attrList)
	c['tempId'] = 1
	c['tempMailId'] = 1
	c['tempGetId'] = 1
	c['tempCustId'] = 1
	insertMenuContent(nodeList, menupopup, False, '3', False)
	createSubElement('menuseparator', menupopup, {'id':c['internalName'] + 'SepOptions3', 'tooltiptext':''})
	createSubElement('menuitem', menupopup, {'id':c['internalName'] + 'Options3', 'class':'menu-iconic ' + c['internalName'] + '-o', 'label':'Options...', 'tooltiptext':'', 'oncommand':'window.openDialog("chrome://' + c['internalName'] + '/content/prefs.xul","' + c['internalName'] + ' - Options","chrome,resizable=yes,centerscreen");'})
	return doc

def chromeManifest():
	"""
	Create the content of the chrome.manifest file
	"""
	doc = c['logPreamble']
	doc += chromeManifestContent.replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
	doc += 'locale	' + c['internalName'] + '	' + c['defaultLocale'] + '	jar:chrome/' + c['internalName'] + '.jar!/locale/' + c['defaultLocale'] + '/' + c['internalName'] + '/\n'
	for locale in c['locales'].keys():
		if locale != c['defaultLocale']:
			doc += 'locale	' + c['internalName'] + '	' + locale + '	jar:chrome/' + c['internalName'] + '.jar!/locale/' + locale + '/' + c['internalName'] + '/\n'
	return doc

def preferencesJs():
	"""
	Create the content of the .js file with preferences in 'default' dir
	"""
	doc = c['cssjsPreamble']
	doc += 'pref("extensions.' + c['id'] + '.description","chrome://' + c['internalName'] + '/locale/' + c['internalName'] + '.properties");\n' + \
	'pref("extensions.' + c['internalName'] + '.TitleMenu", true);\n' + \
	'pref("extensions.' + c['internalName'] + '.ToolsMenu", true);\n' + \
	'pref("extensions.' + c['internalName'] + '.ContextMenu", true);\n' + \
	'pref("extensions.' + c['internalName'] + '.Options", true);\n'
	if c['logo']:
		doc += 'pref("extensions.' + c['internalName'] + '.ShowLogo", true);\n'
	for menu in c['menu']:
		doc += 'pref("extensions.' + c['internalName'] + '.SubMenu' + menu + '", true);\n'
	for t in c['customPages']:
		doc += 'pref("extensions.' + c['internalName'] + '.CustomPage' + t[0] + '", "");\n'
	return doc

def properties(locale):
	"""
	Create the content of the .properties file for the give 'locale'
	"""
	doc = c['logPreamble']
	doc += 'extensions.' + c['id'] + '.description = ' + c[locale + 'Desc']
	return doc

def commonJs():
	"""
	Create the content of the common.js file
	"""
	doc = c['cssjsPreamble']
	if c['logo']:
		text = commonJsMain.replace('@@COMMON_SHOW_LOGO@@', commonJsShowLogo)
	else:
		text = commonJsMain.replace('@@COMMON_SHOW_LOGO@@', '')
	menuLoad = ''
	for menu in c['menu']:
		menuLoad += commonJsMenuBoolLoad.replace('@@MENU_ID@@', menu)
	moreFunctions = ''
	for k, v in c['mailMenu'].items():
		moreFunctions += commonJsMailArchive.replace('@@MAIL_ARCHIVE_ID@@', k).replace('@@MAIL_ARCHIVE_BASE_URL@@', v)
	for t in c['customPages']:
		moreFunctions += commonJsPersPage.replace('@@CUSTOM_PAGE_ID@@', t[0]).replace('@@CUSTOM_PAGE_BASE_URL@@', t[1]).replace('@@CUSTOM_PAGE_PREF@@', 'CustomPage' + t[0])
		menuLoad += commonJsMenuCharLoad.replace('@@CUSTOM_PAGE_ID@@', t[0])
	text = text.replace('@@COMMON_MENU_LOAD@@', menuLoad)
	text = text.replace('@@MORE_FUNCTIONS@@', moreFunctions)
	doc += text.replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
	return doc

def openJs():
	"""
	Create the content of the open.js file
	"""
	doc = c['cssjsPreamble']
	text = openJsMain.replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
	getForms = ''
	for k, v in c['getForms'].items():
		getForms += openJsGetForm.replace('@@GET_FORM_ID@@', k).replace('@@GET_FORM_BASE_URL@@', v)
	doc += text.replace('@@MORE_FUNCTIONS@@', getForms)
	return doc

def prefsJs():
	"""
	Create the content of the prefs.js file
	"""
	doc = c['cssjsPreamble']
	text = prefsJsMain.replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
	menuLoad = ''
	manuSave = ''
	if c['logo']:
		menuLoad += prefsJsBoolLoad.replace('@@PREFS_MENU_ID@@', 'ShowLogo')
		manuSave += prefsJsBoolSave.replace('@@PREFS_MENU_ID@@', 'ShowLogo')
	for menu in c['menu']:
		menuLoad += prefsJsBoolLoad.replace('@@PREFS_MENU_ID@@', 'SubMenu' + menu)
		manuSave += prefsJsBoolSave.replace('@@PREFS_MENU_ID@@', 'SubMenu' + menu)
	for t in c['customPages']:
		menuLoad += prefsJsCharLoad.replace('@@PREFS_MENU_ID@@', 'CustomPage' + t[0])
		manuSave += prefsJsCharSave.replace('@@PREFS_MENU_ID@@', 'CustomPage' + t[0])
	text = text.replace('@@PREFS_LOAD_PREFS@@', menuLoad)
	text = text.replace('@@PREFS_SAVE_PREFS@@', manuSave)
	doc += text
	return doc

def changelog(locale):
	"""
	Create the content of the CHANGELOG files in all locales
	"""
	doc = c['logPreamble']
	if c['changelogs'][locale]:
		if len(c[locale + 'Name']) < 70:
			doc += c[locale + 'Name'].rjust((70 + len(c[locale + 'Name'])) / 2) + '\n\n'
		else:
			doc += wrapText(c[locale + 'Name'])
		for item in c['changelogs'][locale]:
			doc += item[0] + c['logSeparator'][0] + wrapText(item[1]) + c['logSeparator'][1]
	return doc

def buildXml():
	"""
	Create the ElementTree XML API structure of the build.xml file
	"""
	project = etree.Element('project', {'name':c['name'], 'default':'installxpi'})
	target = createSubElement('target', project, {'name':'init'})
	createSubElement('property', target, {'name':'temp', 'value':'temp'})
	createSubElement('property', target, {'name':'version', 'value':c['version']})
	target2 = createSubElement('target', project, {'name':'preparejar', 'depends':'init'})
	createSubElement('mkdir', target2, {'dir':'${temp}'})
	createSubElement('delete', target2, {'file':c['internalName'] + '.jar'})
	copy = createSubElement('copy', target2, {'todir':'${temp}', 'overwrite':'true'})
	fileset = createSubElement('fileset', copy, {'dir':'chrome/'})
	createSubElement('include', fileset, {'name':'content/**'})
	createSubElement('include', fileset, {'name':'locale/**'})
	createSubElement('include', fileset, {'name':'skin/**'})
	target3 = createSubElement('target', project, {'name':'createxpi', 'depends':'preparejar'})
	createSubElement('zip', target3, {'destfile':c['internalName'] + '.jar', 'basedir':'${temp}', 'compress':'false'})
	ziptag = createSubElement('zip', target3, {'destfile':c['internalName'] + '-' + c['version'] + '.xpi'})
	createSubElement('zipfileset', ziptag, {'dir':'.', 'includes':c['internalName'] + '.jar', 'prefix':'chrome/'})
	createSubElement('zipfileset', ziptag, {'dir':'.', 'includes':'chrome.manifest'})
	createSubElement('zipfileset', ziptag, {'dir':'.', 'includes':'install.rdf'})
	createSubElement('zipfileset', ziptag, {'dir':'.', 'includes':'LICENSE'})
	createSubElement('zipfileset', ziptag, {'dir':'.', 'includes':'defaults/**'})
	createSubElement('delete', target3, {'dir':'temp'})
	target4 = createSubElement('target', project, {'name':'installxpi', 'depends':'createxpi'})
	exectag = createSubElement('exec', target4, {'dir':'.', 'executable':'cmd.exe'})
	createSubElement('arg', exectag, {'line':'/c ' + c['internalName'] + '-${version}.xpi'})
	target5 = createSubElement('target', project, {'name':'createsrc', 'depends':'init'})
	ziptag2 = createSubElement('zip', target5, {'destfile':c['internalName'] + '-${version}-src.zip'})
	createSubElement('zipfileset', ziptag2, {'dir':'.', 'includes':'**', 'excludes':'*.jar,*.xpi,*.zip,dev/**'})
	return project

def createDebianDiff():
	"""
	Create the content of the .diff.gz file
	"""
	c['debExtDesc'] = ''
	descLines = c['description'].splitlines()
	c['debControlLenght'] = str(16 + len(descLines))
	for line in descLines:
		if line:
			c['debExtDesc'] += '+ ' + line + '\n'
		else:
			c['debExtDesc'] += '+ .\n'
	c['debExtDesc'] += '+'
	c['debExtAuthor'] = c['author'] + ' <' + c['authorEmail'] + '>'
	c['debIconLicense'] = ''
	for line in c['iconLicense'].splitlines():
		sublines = wrapText(line)
		for subline in sublines.splitlines():
			c['debIconLicense'] += '+' + subline + '\n'
	c['debianChangelog'] = ''
	changelogLines = c['debChangelog'].splitlines()
	c['debChangelogLenght'] = str(1 + len(changelogLines))
	for line in changelogLines:
		c['debianChangelog'] += '+' + line + '\n'
	c['debianChangelog'] += '+'
	c['debIconLicense'] = '+\n'
	if c['iconLicense']:
		copyLines = c['iconLicense'].splitlines()
		c['debCopyrightLenght'] = str(36 + len(copyLines))
		for line in copyLines:
			c['debIconLicense'] += '+' + line + '\n'
		c['debIconLicense'] += '+'
	doc = debianDiffMain
	for k, v in debianDiffChanges.items():
		doc = doc.replace(k, c[v])
	return doc

if __name__ == '__main__':
	sys.exit(__doc__)
