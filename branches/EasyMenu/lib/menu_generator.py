#===================================================================#
# Program: Easy Menu v. 1.0.3
# Short description: a multi-browser automagic extension builder
# Online resources: http://easymenu.googlepages.com/
#                   https://launchpad.net/easymenu
# File: menu_generator.py
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
-t, --test             Check the validity of the source input and exit
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

try:
	import sys
	import optparse
	import os
	import re
	import shutil
	import imghdr
	import codecs
	import time
	import zipfile
	import tarfile
	import gzip
	import StringIO
	from datetime import datetime, timedelta
	from xml.etree import ElementTree as etree

	from lxml import etree as letree

	from contents import *
	from files_generator import *
except ImportError, detail:
	sys.exit(' ERROR - MODULE NOT FOUND: ' + str(detail) + '\n -- EXIT --')

def parseCommandLine(argv):
	"""
	Parse the command line input
	"""
	# Get description and usage from the first two paragraphs of the docstring
	app_info = __doc__.split('\n\n')
	parser = optparse.OptionParser(description=app_info[0], usage=app_info[1])
	# Populate the option parser
	parser.add_option('-t', '--test', action='store_true')
	parser.add_option('-v', '--version', action='store_true')
	parser.add_option('-c', '--compatibility')
	parser.add_option('-o', '--overwrite', action='store_true')
	parser.add_option('-s', '--source', action='store_true')
	parser.add_option('-d', '--debian', action='store_true')

	options, parameters = parser.parse_args(argv)

	if options.version:
		sys.exit()

	if not options.compatibility or options.compatibility in ('s', 'p', 't'):
		c['compatibility'] = options.compatibility
	else:
		sys.exit(__doc__)

	c['testsource'] = options.test
	c['overwrite'] = options.overwrite
	c['source'] = options.source
	c['debian'] = options.debian

	if len(parameters) == 0:
		sys.exit(__doc__)
	return parameters

def indentXml(doc, level=0):
	"""
	Indent the XML structure of the ElementTree XML API object 'doc'
	This function was written by effbot and available here:
	http://effbot.python-hosting.com/file/effbotlib/ElementTree.py
	It was released under 'an old-style Python license', so compatible
	with the GNU GPL as stated by the GNU Project here:
	http://www.gnu.org/licenses/license-list.html
	"""
	i = "\n" + level*"  "
	if len(doc):
		if not doc.text or not doc.text.strip():
			doc.text = i + "  "
		for e in doc:
			indentXml(e, level+1)
		if not e.tail or not e.tail.strip():
			e.tail = i
	if level and (not doc.tail or not doc.tail.strip()):
		doc.tail = i

def saveXmlFile(destFile, doc, doctype=False, sub={}, pi=False):
	"""
	Save the ElementTree XML API object 'doc' to
	the utf-8 encoded file 'destFile', making all
	the substitutions of the 'sub' dictionary, if any.
	The standard processing instruction will be added
	based on the boolean 'pi'.
	"""
	try:
		indentXml(doc)
		content = etree.ElementTree(doc)
		file = open(c['dirName'] + '/' + destFile, 'w')
		tmpFile = os.tmpfile()
		content.write(tmpFile, 'utf8')
		tmpFile.seek(0)
		head = tmpFile.readline()
		content = tmpFile.read()
		tmpFile.close()
		preamble = c['xmlDeclaration'] + '\n<!--\n' + c['preamble'] + '-->\n'
		if pi:
			preamble += '\n' + c['processingInstruction']
		if doctype:
			preamble += '\n' + c['doctype']
		text = preamble + '\n' + content
		for k, v in sub.items():
			text = text.replace(k.encode('utf-8'), v.encode('utf-8'))
		file.write(text)
		file.close()
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to create "' + c['dirName'] + '/' + destFile + '" file\n -- EXIT --')

def saveFile(destFile, text):
	"""
	Save the utf-8 encoded file 'destFile' with 'text' as content
	"""
	try:
		file = codecs.open(c['dirName'] + '/' + destFile, 'w', 'utf-8')
		file.write(text)
		file.close()
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to create "' + c['dirName'] + '/' + destFile + '" file\n -- EXIT --')

def openAnything(source):
	"""
	This function lets you define parsers that take any input source
	(URL, pathname to local or network file, or actual data as a string)
	and deal with it in a uniform manner. Returned object is guaranteed
	to have all the basic stdio read methods (read, readline, readlines).
	Just .close() the object when you're done with it.
	"""
	c['openAnythingResult'] = ''
	# check if source is already a valid file object
	if hasattr(source, 'read'):
		return source

	c['openAnythingResult'] = ' - Check if source is set to standard input: '
	if source == '-':
		return StringIO.StringIO(str(sys.stdin.read()))
	else:
		print c['openAnythingResult'] + 'no'

	# try to open with native open function (if source is pathname)
	c['openAnythingResult'] = ' - Check if source is a regular file: '
	try:
		return open(source, 'r')
	except (IOError, OSError):
		print c['openAnythingResult'] + 'no'

	# try to open with urllib (if source is http, ftp, or file URL)
	c['openAnythingResult'] = ' - Check if source is a valid URL: '
	import urllib
	try:
		return urllib.urlopen(source)
	except (IOError, OSError):
		print c['openAnythingResult'] + 'no'

	# treat source as string
	c['openAnythingResult'] = ''
	print ' - Treat source as an input string'
	return StringIO.StringIO(str(source))

def validateXml(f, xsdFilename):
	"""
	Validate the XML input with the external XML Schema file 'xsdFilename'
	and some other manual checks.
	If the XML file is not valid, an error message will be printed.
	"""
	lxmlParsed = letree.parse(f)
	f.seek(0)
	try:
		file = open(xsdFilename)
		xsdFile = letree.parse(file)
		xsd = letree.XMLSchema(xsdFile)
		file.close()
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to open XML Schema file "' + xsdFilename + '"\n -- EXIT --')
	validity = xsd.validate(lxmlParsed)
	errors = str(xsd.error_log).splitlines()
	
	if not validity:
		c['testPassed'] = False
		if errors:
			errorsMessage = ' ERROR - The XML input is not valid:\n  |====>   ' + '\n  |====>   '.join(errors)
			if c['testsource']:
				print errorsMessage
			else:
				sys.exit(errorsMessage + '\n -- EXIT --')

def setCompatibilityMaxVersion():
	"""
	Set the maxVersion compatibility values accordingly to the user choice
	"""
	if not c['compatibility']:
		print ' QUESTION - What compatibility max version must be used? (s/p/t)'
		print ' ======> - s => Standard (Firefox ' + c['ffoxMaxVersion']['s'] + ' | Flock ' + c['flockMaxVersion']['s'] + ')'
		print ' ======> - p => Packaging (Firefox ' + c['ffoxMaxVersion']['p'] + ' | Flock ' + c['flockMaxVersion']['p'] + ')'
		print ' ======> - t => Testing (Firefox ' + c['ffoxMaxVersion']['t'] + ' | Flock ' + c['flockMaxVersion']['t'] + ')'
		compatibility = raw_input(' ')
		if compatibility in ('s', 'p', 't'):
			c['compatibility'] = compatibility
		else:
			sys.exit(' ERROR - Invalid reply\n -- EXIT --')

	print ' - ' + c['compatibilities'][c['compatibility']] + ' max version compatibility choosed'

def createFolders():
	"""
	Check for existent final '.xpi' and '.tar.gz' compressed
	archives and ask for replacement.
	Check for existent main folder and ask for replacement,
	then create all the folders essentials to the extension
	creation process.
	"""
	if os.path.isfile(c['dirName'] + '.xpi'):
		if c['overwrite']:
			choose = 'y'
		else:
			print ' WARNING - The file with the name "' + c['dirName'] + '.xpi" already exist'
			print ' ======> - Delete the existing one? (y/n)'
			choose = raw_input(' ')
		if choose.lower() == 'y':
			try:
				os.remove(c['dirName'] + '.xpi')
			except (IOError, OSError):
				sys.exit(' ERROR - Unable to delete "' + c['dirName'] + '.xpi" file\n -- EXIT --')
		elif choose.lower() == 'n':
			sys.exit(' ERROR - Unable to write output, move, rename or delete "' + c['dirName'] + '.xpi" file and retry\n -- EXIT --')
		else:
			sys.exit(' ERROR - Invalid reply\n -- EXIT --')

	if os.path.isfile(c['dirName'] + '.tar.gz'):
		if c['overwrite']:
			choose = 'y'
		else:
			print ' WARNING - The file with the name "' + c['dirName'] + '.tar.gz" already exist'
			print ' ======> - Delete the existing one? (y/n)'
			choose = raw_input(' ')
		if choose.lower() == 'y':
			try:
				os.remove(c['dirName'] + '.tar.gz')
			except (IOError, OSError):
				sys.exit(' ERROR - Unable to delete "' + c['dirName'] + '.tar.gz" file\n -- EXIT --')
		elif choose.lower() == 'n':
			sys.exit(' ERROR - Unable to write output, move, rename or delete "' + c['dirName'] + '.tar.gz" file and retry\n -- EXIT --')
		else:
			sys.exit(' ERROR - Invalid reply\n -- EXIT --')

	if os.path.isdir(c['dirName']):
		if c['overwrite']:
			choose = 'y'
		else:
			print ' WARNING - A directory with the name "' + c['dirName'] + '" already exist'
			print ' ======> - Delete the existing one and all it\'s content? (y/n)'
			choose = raw_input(' ')
		if choose.lower() == 'y':
			for root, dirs, files in os.walk(c['dirName'], topdown=False):
				for name in files:
					try:
						os.remove(os.path.join(root, name))
					except (IOError, OSError):
						sys.exit(' ERROR - Unable to delete "' + os.path.join(root, name) + '" file\n -- EXIT --')
				for name in dirs:
					try:
						os.rmdir(os.path.join(root, name))
					except (IOError, OSError):
						sys.exit(' ERROR - Unable to delete "' + os.path.join(root, name) + '" directory\n -- EXIT --')
			try:
				os.rmdir(c['dirName'])
			except (IOError, OSError):
				sys.exit(' ERROR - Unable to delete "' + c['dirName'] + '" directory\n -- EXIT --')
			print ' - Existing directory deleted'
		elif choose.lower() == 'n':
			sys.exit(' ERROR - Unable to write output, move, rename or delete "' + c['dirName'] + '" directory and retry\n -- EXIT --')
		else:
			sys.exit(' ERROR - Invalid reply\n -- EXIT --')

	try:
		os.makedirs(c['dirName'] + '/defaults/preferences')
		os.makedirs(c['dirName'] + '/chrome/content/' + c['internalName'])
		os.makedirs(c['dirName'] + '/chrome/skin/classic/' + c['internalName'] + '/icons')
		for locale in c['locales'].keys():
			os.makedirs(c['dirName'] + '/chrome/locale/' + locale + '/' + c['internalName'])
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to create "' + c['dirName'] + '" directory or their sub-directories\n -- EXIT --')
	print ' - New source file structure created in "' + c['dirName'] + '" directory'

def popolateContents(extensionTag):
	"""
	Analyse the main 'extension' tag in the XML input
	and fill a series of useful global variables
	used everywhere.
	"""
	c['extensionNames'] = extensionTag.attrib
	c['year'] = str(datetime.utcnow())[:4]
	c['id'] =  extensionTag.findtext('id')
	c['datetime'] = str(datetime.utcnow())[:-7]
	c['debDateTime'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
	c['name'] = extensionTag.findtext('name')
	c['description'] = wrapText(extensionTag.findtext('en-description'))
	oneLineDesc = extensionTag.findtext('en-description').splitlines()[0]
	if len(oneLineDesc) > 77:
		oneLineDesc = oneLineDesc[:77] + '...'
	c['oneLineDesc'] = oneLineDesc
	if extensionTag.find('en-icon-license') != None:
		c['iconLicense'] = c['iconLicensePreamble'] + extensionTag.findtext('en-icon-license')
	c['internalName'] = 'em_' + c['extensionNames']['short-name'].replace('-', '')
	c['version'] = c['extensionNames']['version']
	c['dirName'] = 'em_' + c['extensionNames']['short-name'] + '_' + c['version']
	c['author'] =  extensionTag.findtext('author-name')
	c['authorEmail'] =  extensionTag.findtext('author-email')
	if extensionTag.find('author-url') != None:
		c['authorUrl'] = extensionTag.findtext('author-url')
	c['homepageURL'] = extensionTag.findtext('homepageURL')
	if extensionTag.find('icon') != None:
		logo = extensionTag.findtext('icon')
		install['icon'] = install['icon'].replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])
		c['logo'] = logo
	c['locale'] = c['dirName'] + '/chrome/locale/@@LOCALE_ID@@/' + c['internalName'] + '/' + c['internalName']
	c['defaultLocale'] = extensionTag.find('localized').attrib['locale']
	for locale in extensionTag.findall('localized'):
		localeId = locale.attrib['locale']
		c['locales'][localeId] = locale.findtext('locale-name')
		if locale.find('name') != None:
			c[localeId + 'Name'] = locale.findtext('name')
		else:
			c[localeId + 'Name'] = c['name']
		c[localeId + 'Desc'] = locale.findtext('description')
		c['changelogs'][localeId] = []
		try:
			for node in locale.find('menu-changelog').getchildren():
				c['changelogs'][localeId].append((node.attrib['version'] + ' - ' + node.attrib['date'], node.text))
		except AttributeError:
			pass
	if len(c['name']) < 70:
		c['licenseName'] = c['name'].rjust((70 + len(c['name'])) / 2)
	else:
		c['licenseName'] = wrapText(c['name'])
	c['licenseCopyright'] = c['licenseCopyright'].replace('@@YEAR@@', c['year'])
	c['licenseCopyright'] = c['licenseCopyright'].replace('@@AUTHOR@@', c['author'])
	c['licenseCopyright'] = c['licenseCopyright'].replace('@@AUTHOR_EMAIL@@', c['authorEmail'])
	if len(c['licenseCopyright']) < 70:
		c['licenseCopyright'] = c['licenseCopyright'].rjust((70 + len(c['licenseCopyright'])) / 2)
	else:
		c['licenseCopyright'] = wrapText(c['licenseCopyright'])
	if c['debian']:
		debian = extensionTag.find('debian')
		if debian != None:
			c['packageName'] = debian.findtext('package-name')
			c['maintainer'] = debian.findtext('maintainer')
			c['origMaintainer'] = debian.findtext('orig-maintainer')
			c['watchDir'] = debian.findtext('watch-dir')
			c['shortDesc'] = debian.findtext('one-line-desc').splitlines()[0]
			c['bzrBranch'] = debian.findtext('bzr-branch')
			c['debChangelog'] = debian.findtext('deb-changelog')
		else:
			sys.exit(' ERROR - Unable to found "debian" tag in XML input while using option -d (--debian)\n -- EXIT --')
	c['doctype'] = c['doctype'].replace('@@EXTENSION_INTERNAL_NAME@@', c['internalName'])

def initializePreambles():
	"""
	Initialize the copyright preamble variable to the
	different file format adding the correct comment tags
	before and after and making a list of substitutions.
	"""
	for k, v in c['preambleReplacements'].items():
		c['preamble'] = c['preamble'].replace(k, c[v])
	c['cssjsPreamble'] = '/*\n' + c['preamble'] + '*/\n\n'
	logSeparator = '#=======================================================================#\n'
	c['logPreamble'] = logSeparator + re.sub('\n', '\n#', re.sub('^', '#', c['preamble'])) + '\n' + logSeparator + '\n'
	for k, v in c['licenseSubstitutions'].items():
		c['license'] = c['license'].replace(k, c[v])

def listInList(list1, list2):
	"""
	Find if all elements of 'list1' are also
	in 'list2'.
	Return a string with the list of differences
	comma separated, empty string otherwise.
	"""
	diff = ''
	for item in list1:
		if item not in list2:
			diff += item + ', '
	return diff

def initializeIcons(menuTag):
	"""
	Analyse the 'icons' folder to find all the '.png' images
	and the XML input checking that all the called icons
	are really available in the 'icons' folder.
	"""
	# analize the 'icons' folder
	noIcons = False
	try:
		iconList = os.listdir('icons')
	except (IOError, OSError):
		noIcons = True
		iconListNames = []

	if not noIcons:
		[iconList.remove(k) for k in iconList if os.path.splitext(k)[1] != '.png']
		[iconList.remove(k) for k in iconList if imghdr.what('icons/' + k) != 'png']
		iconListNames = [k[:-4] for k in iconList]

	# analize icons tags in the XML input
	noXmlIcons = False
	iconXmlTags = menuTag.getiterator('icon')
	iconXmlNames = list(set([icon.text for icon in iconXmlTags]))
	if c['logo']:
		iconXmlNames.append(c['logo'])
	for item in menuTag.getiterator('mailmenu'):
		if item.attrib['icons'].lower() == 'true':
			c['showMailIcons'] = True
			[iconXmlNames.append('ml_' + mailIcon) for mailIcon in c['mailIcons']]
			break

	if len(iconXmlNames) == 0:
		noXmlIcons = True

	if noXmlIcons:
		if c['testsource']:
			print ' WARNING - No menu icons are specified in the XML input'
			return
		else:
			print ' WARNING - No menu icons specified in the XML input. Proceed anyway without icons? (y/n)'
			choose = raw_input(' ')
			if choose.lower() == 'no':
				sys.exit(' ERROR - Program interrupted by the user\n -- EXIT --')
			elif choose.lower() == 'y':
				pass
			else:
				sys.exit(' ERROR - Invalid reply\n -- EXIT --')
	else:
		listDiff = listInList(iconXmlNames, iconListNames)
		if listDiff:
			listDiffMessage = ' ERROR - The following icons are specified in the XML input but they aren\'t in the "icons" folder:\n ====> - ' + listDiff[:-2]
			if c['testsource']:
				print listDiffMessage
				c['testPassed'] = False
				return
			else:
				sys.exit(listDiffMessage + '\n -- EXIT --')
		else:
			if c['testsource']:
				print ' - Icons check: done'
				return
		i = 1
		for icon in iconXmlNames:
			try:
				shutil.copy('icons/' + icon + '.png', c['dirName'] + '/chrome/skin/classic/' + c['internalName'] +'/icons/' + str(i) + '.png')
				c['icons'][icon] = str(i)
				i += 1
			except (IOError, OSError):
				sys.exit(' ERROR - Unable to copy the "icons/' + icon + '.png" image to "' + c['dirName'] + '/chrome/skin/classic/' + c['internalName'] + '/icons/" folder\n -- EXIT --')

	if c['showMailIcons']:
		for icon in c['mailIcons']:
			try:
				shutil.copy('icons/ml_' + icon + '.png', c['dirName'] + '/chrome/skin/classic/' + c['internalName'] + '/icons/ml_' + icon + '.png')
			except (IOError, OSError):
				sys.exit(' ERROR - Unable to copy one of the Mail Menu icons file to the relative destination folder\n -- EXIT --')

	if c['logo']:
		try:
			shutil.copy('icons/' + c['logo'] + '.png', c['dirName'] + '/chrome/skin/classic/' + c['internalName'] + '/logo.png')
		except (IOError, OSError):
			sys.exit(' ERROR - Unable to copy the "icons/' + c['logo'] + '.png" image to "' + c['dirName'] + '/chrome/skin/classic/' + c['internalName'] + '/logo.png"\n -- EXIT --')

	try:
		shutil.copy('lib/options.png', c['dirName'] + '/chrome/skin/classic/' + c['internalName'] + '/icons/options.png')
		shutil.copy('lib/GPLv3License.txt', c['dirName'] + '/chrome/content/' + c['internalName'] + '/')
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to copy "lib/options.png" or "lib/GPLv3License.txt" file to the relative destination folder\n -- EXIT --')

def initializeMainMenu(nodeList):
	"""
	Process the direct child list of the 'main-menu' tag in the XML input
	"""
	for node in nodeList:
		n = node.tag
		if n == 'bgcolor':
			if node.attrib.has_key('border'):
				bo = node.attrib['border'].lower()
				c['boColMenu'] = bo
				c['boColors'].append(bo)
			bg = node.text.lower()
			c['bgColMenu'] = bg
			c['bgColors'].append(bg)
		elif n == 'icon':
			c['iconTitle'] = node.text
		elif n == 'itemname':
			addDtdEntry(node, 'MenuName')
		elif n == 'tooltiptext':
			addDtdEntry(node, 'MenuName_t')
			c['tooltiptext'] = True
		elif n == 'content':
			return node.getchildren()

def createJar():
	"""
	Create the temporary .jar compressed archive
	in the 'chrome' directory.
	"""
	try:
		jarFile = zipfile.ZipFile(c['dirName'] + '/' + c['internalName'] + '.jar', 'w')
		dirNameLenght = len(c['dirName'])
		for root, dirs, files in os.walk(c['dirName'] + '/chrome', topdown=False):
			for name in files:
				archiveFileName = os.path.join(root, name)[dirNameLenght + 8:]
				jarFile.write(os.path.join(root, name).encode('utf-8'), archiveFileName.encode('utf-8'), zipfile.ZIP_DEFLATED)
		jarFile.close()
		shutil.move(c['dirName'] + '/' + c['internalName'] + '.jar', c['dirName'] + '/chrome/' + c['internalName'] + '.jar')
	except (UnicodeDecodeError, TypeError, IOError, OSError):
		sys.exit(' ERROR - Unable to create compressed JAR file "' + c['dirName'] + '/chrome/' + c['internalName'] + '.jar"\n -- EXIT --')

def createXpi():
	"""
	Create the final .xpi compressed archive to be directly
	imported into the browser.
	"""
	try:
		xpiFile = zipfile.ZipFile(c['dirName'] + '.xpi', 'w')
		fileList = ['chrome.manifest', 'install.rdf', 'LICENSE', 'defaults/preferences/' + c['internalName'] + '.js', 'chrome/' + c['internalName'] + '.jar']
		for file in fileList:
			fileName = c['dirName'] + '/' + file
			xpiFile.write(fileName.encode('utf-8'), file.encode('utf-8'), zipfile.ZIP_DEFLATED)
		xpiFile.close()
	except (UnicodeDecodeError, TypeError, IOError, OSError):
		sys.exit(' ERROR - Unable to create compressed XPI file "' + c['dirName'] + '.xpi"\n -- EXIT --')

def removeTempFiles():
	"""
	Remove the temporary .jar file in 'chrome' folder
	"""
	try:
		os.remove(c['dirName'] + '/chrome/' +  c['internalName'] + '.jar')
	except (IOError, OSError):
		sys.exit(' ERROR - Unable to delete temporary JAR file "' + c['dirName'] + '/chrome/' + c['internalName'] + '.jar"\n -- EXIT --')

def createTarGz(orig):
	"""
	Create a TarGz archive with the source files of the extension
	"""
	ext = '.tar.gz'
	if orig:
		ext = '.orig.tar.gz'
	try:
		tarGzFile = tarfile.open(c['dirName'] + ext, 'w:gz')
		tarGzFile.add(c['dirName'])
		tarGzFile.close()
	except (UnicodeDecodeError, TypeError, IOError, OSError):
		sys.exit(' ERROR - Unable to create compressed TAR-GZ file "' + c['dirName'] + ext + '"\n -- EXIT --')

def createDiffGz(text):
	"""
	Create a .diff.gz compressed archive of the 'debian' folder files
	"""
	try:
		gzFile = gzip.open(c['dirName'] + '.diff.gz', 'wb')
		gzFile.write(text.encode('utf-8'))
		gzFile.close()
	except (UnicodeDecodeError, TypeError, IOError, OSError):
		sys.exit(' ERROR - Unable to create compressed GZ file "' + c['dirName'] + '.diff.gz"\n -- EXIT --')

def main(argv):
	"""
	Main function of Easy Menu that execute
	the whole extension building process.
	"""
	source = parseCommandLine(argv)[0]
	if c['testsource']:
		print ' -- RUNNING IN TEST MODE'
	f = openAnything(source)
	if c['openAnythingResult']:
		print c['openAnythingResult'] + 'yes'

	validateXml(f, 'lib/validator.xsd')
	print ' - Check XML source validity with XML Schema file: done'

	if not c['testPassed']:
		sys.exit(' -- TEST RESULT: FAILED\n\n --------  FINISHED  --------\n')

	xmlParsed = etree.parse(f)
	f.close()
	print ' - Parse XML file: done'

	extensionTag = xmlParsed.find('extension')
	menuTag = xmlParsed.find('main-menu')
	popolateContents(extensionTag)
	initializePreambles()
	if not c['testsource']:
		createFolders()
	initializeIcons(menuTag)
	if c['testsource']:
		if c['testPassed']:
			sys.exit(' -- TEST RESULT: PASSED\n\n --------  FINISHED  --------\n')
		else:
			sys.exit(' -- TEST RESULT: FAILED\n\n --------  FINISHED  --------\n')

	setCompatibilityMaxVersion()
	print ' - Creating extension files...'
	saveFile('LICENSE', c['license'])
	saveFile('chrome.manifest', chromeManifest())
	saveFile('chrome/content/' + c['internalName'] + '/LICENSE', c['license'])
	saveXmlFile('install.rdf', installRdf(extensionTag))
	saveXmlFile('chrome/skin/classic/' + c['internalName'] + '/contents.rdf', skinContentsRdf())
	for k, v in c['locales'].items():
		localePreamble = '<!--\n' + c['preamble'] + '-->\n'
		saveFile('chrome/locale/' + k + '/' + c['internalName'] + '/' + c['internalName'] + '.dtd', localePreamble)
		saveXmlFile('chrome/locale/' + k + '/' + c['internalName'] + '/contents.rdf', localeContentsRdf(k, v))
		saveFile('chrome/locale/' + k + '/' + c['internalName'] + '/' + c['internalName'] + '.properties', properties(k))
		saveFile('chrome/locale/' + k + '/' + c['internalName'] + '/' + 'CHANGELOG', changelog(k))
	mainContentList = initializeMainMenu(menuTag.getchildren())
	saveFile('chrome/content/' + c['internalName'] + '/url.properties', c['logPreamble'] + c['internalName'] + '.url.fake=\n')
	saveXmlFile('chrome/content/' + c['internalName'] + '/about.xul', aboutXul(), True, {'@@INTERNAL_ENTITY_NAME@@':'&' + c['internalName']}, True)
	saveXmlFile('chrome/content/' + c['internalName'] + '/contents.rdf', contentContentsRdf())
	saveXmlFile('chrome/content/' + c['internalName'] + '/titleMenu.xul', titleMenuXul(mainContentList), True, {'@@INTERNAL_ENTITY_NAME@@':'&' + c['internalName']})
	saveXmlFile('chrome/content/' + c['internalName'] + '/toolsMenu.xul', toolsMenuXul(mainContentList), True, {'@@INTERNAL_ENTITY_NAME@@':'&' + c['internalName']})
	saveXmlFile('chrome/content/' + c['internalName'] + '/contextMenu.xul', contextMenuXul(mainContentList), True, {'@@INTERNAL_ENTITY_NAME@@':'&' + c['internalName']})
	saveXmlFile('chrome/content/' + c['internalName'] + '/prefs.xul', prefsXul(), True, {'@@INTERNAL_ENTITY_NAME@@':'&' + c['internalName']}, True)
	saveFile('chrome/skin/classic/' + c['internalName'] + '/' + c['internalName'] + '.css', createCss())
	saveFile('defaults/preferences/' + c['internalName'] + '.js', preferencesJs())
	saveFile('chrome/content/' + c['internalName'] + '/common.js', commonJs())
	saveFile('chrome/content/' + c['internalName'] + '/open.js', openJs())
	saveFile('chrome/content/' + c['internalName'] + '/prefs.js', prefsJs())

	finalMessage = '\n --------  FINISHED  --------\n\n Extension "' + c['name'] + '" succesfully generated:\n'
	createJar()
	createXpi()
	removeTempFiles()
	finalMessage += ' - XPI file --------> ' + c['dirName'] + '.xpi\n'
	finalMessage += ' - Source folder ---> ' + c['dirName'] + '/\n'
	if c['source']:
		createTarGz(False)
		finalMessage += ' - Source archive --> ' + c['dirName'] + '.tar.gz\n'
	if c['debian']:
		saveXmlFile('build.xml', buildXml())
		createTarGz(True)
		finalMessage += ' - Debian "orig" archive --> ' + c['dirName'] + '.orig.tar.gz\n'
		createDiffGz(createDebianDiff())
		finalMessage += ' - Debian "diff" archive --> ' + c['dirName'] + '.diff.gz\n'
	print finalMessage
	sys.exit()

if __name__ == '__main__':
	sys.exit(__doc__)
