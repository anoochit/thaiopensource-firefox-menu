#===================================================================#
# Program: Easy Menu v. 1.0.3
# Short description: a multi-browser automagic extension builder
# Online resources: http://easymenu.googlepages.com/
#                   https://launchpad.net/easymenu
# File: contents.py
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

c = {}
c['emSite'] = 'http://easymenu.googlepages.com/'
c['emVersion'] = '1.0.3'
c['locales'] = {}
c['logo'] = ''
c['testsource'] = False
c['testPassed'] = True
c['overwrite'] = False
c['source'] = False
c['debian'] = False
c['authorUrl'] = ''
c['compatibilities'] = {'s':'Standard', 'p':'Packaging', 't':'Testing'}
c['ffoxMinVersion'] = '1.5'
c['ffoxMaxVersion'] = {'s':'3.0.*', 'p':'3.1.*', 't':'3.1.*'}
c['flockMinVersion'] = '0.4'
c['flockMaxVersion'] = {'s':'1.2.*', 'p':'1.2.*', 't':'2.*'}
c['preambleReplacements'] = {'@@EXTENSION_NAME@@':'name', '@@EM_VERSION@@':'emVersion', '@@EXTENSION_INTERNAL_NAME@@':'internalName', '@@EM_SITE@@':'emSite', '@@DATE@@':'datetime'}
c['xmlDeclaration'] =  '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
c['doctype'] = '<!DOCTYPE overlay SYSTEM "chrome://@@EXTENSION_INTERNAL_NAME@@/locale/@@EXTENSION_INTERNAL_NAME@@.dtd" >'
c['processingInstruction'] = '<?xml-stylesheet href="chrome://global/skin/" type="text/css"?>'
c['titleIcon'] = ''
c['icons'] = {}
c['colors'] = []
c['bgColors'] = []
c['bgColMenu'] = ''
c['boColors'] = []
c['boColMenu'] = ''
c['menu'] = []
c['changelogs'] = {}
c['mailMenu'] = {}
c['mailIcons'] = ['thread', 'subject', 'author', 'date']
c['showMailIcons'] = False
c['getForms'] = {}
c['customPages'] = []
c['tooltiptext'] = False
c['logSeparator'] = ('\n-------------------------------------------------------------------------\n', '\n=========================================================================\n\n')
c['iconLicensePreamble'] = 'As an exception, permission is granted to make use of licensed artwork\nfor the following images in the "icons" folder:\n'
c['iconLicense'] = ''
c['preamble'] = """ This file was automagically generated on @@DATE@@ UTC
 by Easy Menu v. @@EM_VERSION@@ ( @@EM_SITE@@ )
 and is part of '@@EXTENSION_NAME@@'.

 @@EXTENSION_NAME@@ is free software: you can redistribute it
 and/or modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation, either version 3 of
 the License, or (at your option) any later version.

 @@EXTENSION_NAME@@ is distributed in the hope that it will be
 useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with @@EXTENSION_NAME@@.
 If not, see http://www.gnu.org/licenses/.

 The copy of the GNU General Public License can be found here:
 chrome://@@EXTENSION_INTERNAL_NAME@@/content/GPLv3License.txt
"""

c['licenseName'] = ''
c['licenseCopyright'] = 'Copyright (C) @@YEAR@@ @@AUTHOR@@ - @@AUTHOR_EMAIL@@'
c['licenseSubstitutions'] = {'@@EXTENSION_NAME@@':'licenseName', '@@EXTENSION_DESCRIPTION@@':'description', '@@COPYRIGHT_LINE@@':'licenseCopyright', '@@EXTENSION_INTERNAL_NAME@@':'internalName', '@@ICON_LICENSE@@':'iconLicense'}

c['license'] = """@@EXTENSION_NAME@@

@@EXTENSION_DESCRIPTION@@

@@COPYRIGHT_LINE@@

                    - - -    LICENSE    - - -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see http://www.gnu.org/licenses/.

The copy of the GNU General Public License can be found here:
chrome://@@EXTENSION_INTERNAL_NAME@@/locale/GPLv3License.txt
or here: http://www.gnu.org/licenses/gpl.html

You can found translated version of this License here:
http://www.gnu.org/licenses/translations.html

@@ICON_LICENSE@@

"""

install = {}
install['icon'] = 'chrome://@@EXTENSION_INTERNAL_NAME@@/skin/logo.png'
install['aboutURL'] = 'chrome://@@EXTENSION_INTERNAL_NAME@@/content/about.xul'
install['optionsURL'] = 'chrome://@@EXTENSION_INTERNAL_NAME@@/content/prefs.xul'
install['watchURL'] = ''


aboutXulScript = """
		function about_open(url, features)
		{
			const ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"].getService(
				Components.interfaces.nsIWindowWatcher);
			ww.openWindow(window, url, "_blank", features || null, null);
		}"""

chromeManifestContent = """
overlay	chrome://browser/content/browser.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/content/titleMenu.xul
overlay	chrome://browser/content/browser.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/content/toolsMenu.xul
overlay	chrome://browser/content/browser.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/content/contextMenu.xul
overlay	chrome://navigator/content/navigator.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/content/titleMenu.xul
overlay	chrome://global/content/customizeToolbar.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/content/titleMenu.xul
content	@@EXTENSION_INTERNAL_NAME@@	jar:chrome/@@EXTENSION_INTERNAL_NAME@@.jar!/content/@@EXTENSION_INTERNAL_NAME@@/
skin	@@EXTENSION_INTERNAL_NAME@@	classic/1.0	jar:chrome/@@EXTENSION_INTERNAL_NAME@@.jar!/skin/classic/@@EXTENSION_INTERNAL_NAME@@/
style	chrome://browser/content/browser.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/skin/@@EXTENSION_INTERNAL_NAME@@.css
style	chrome://global/content/customizeToolbar.xul	chrome://@@EXTENSION_INTERNAL_NAME@@/skin/@@EXTENSION_INTERNAL_NAME@@.css
"""

commonJsMain = """
window.addEventListener("load", @@EXTENSION_INTERNAL_NAME@@Load, false);

function @@EXTENSION_INTERNAL_NAME@@Load() {
	gBrowser.addProgressListener(@@EXTENSION_INTERNAL_NAME@@Progress);
	@@EXTENSION_INTERNAL_NAME@@Common.onLoad();
}

window.addEventListener("unload", @@EXTENSION_INTERNAL_NAME@@Unload, false);

function @@EXTENSION_INTERNAL_NAME@@Unload() {
	gBrowser.removeProgressListener(@@EXTENSION_INTERNAL_NAME@@Progress);
}

function @@EXTENSION_INTERNAL_NAME@@CheckStatus() {
	var a = @@EXTENSION_INTERNAL_NAME@@Progress.webprog;
	if ((a && !a.isLoadingDocument) || !a)
		@@EXTENSION_INTERNAL_NAME@@Common.onLoad();
}

var @@EXTENSION_INTERNAL_NAME@@Progress = {
	webprog: null,

	QueryInterface: function(aIID) {
		if (aIID.equals(Components.interfaces.nsIWebProgressListener) ||
		aIID.equals(Components.interfaces.nsISupportsWeakReference) ||
		aIID.equals(Components.interfaces.nsISupports))
			return this;
		throw Components.results.NS_NOINTERFACE;
	},

	onLinkIconAvailable: function(a) { },
	onLocationChange: function(a,b,c) {
		this.webprog = a;
		window.setTimeout(@@EXTENSION_INTERNAL_NAME@@CheckStatus,200);
	},

	onProgressChange: function(a,b,c,d,e,f) { },
	onSecurityChange: function(a,b,c) { },
	onStateChange: function(a,b,c,d) {
		if ((a && !a.isLoadingDocument) || !a) {
			@@EXTENSION_INTERNAL_NAME@@Common.onLoad();
		}
	},
	onStatusChange: function(a,b,c,d) { }
};

var @@EXTENSION_INTERNAL_NAME@@Common = {

	getPrefs: function() {
		return Components.classes["@mozilla.org/preferences-service;1"].
		getService(Components.interfaces.nsIPrefService).
		getBranch("extensions.@@EXTENSION_INTERNAL_NAME@@.");
	},

	getMainWin: function() {
		return Components.classes["@mozilla.org/appshell/window-mediator;1"].
		getService(Components.interfaces.nsIWindowMediator).
		getMostRecentWindow("navigator:browser");
	},

	onLoad: function() {
		var prefs = this.getPrefs();
		var win = this.getMainWin();
		var class = 'menu-iconic';
@@COMMON_SHOW_LOGO@@
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@TitleMenu').setAttribute('hidden', !prefs.getBoolPref('TitleMenu'));
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@TitleMenu').setAttribute('class', class);
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@ToolsMenu').setAttribute('hidden', !prefs.getBoolPref('ToolsMenu'));
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@ToolsMenu').setAttribute('class', class);
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@ContextMenu').setAttribute('hidden', !prefs.getBoolPref('ContextMenu'));
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@ContextMenu').setAttribute('class', class);
	},

	onMenuLoad: function(number) {
		var prefs = this.getPrefs();
		var win = this.getMainWin();
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@SepOptions' + number).setAttribute('hidden', !prefs.getBoolPref('Options'));
		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@Options' + number).setAttribute('hidden', !prefs.getBoolPref('Options'));
@@COMMON_MENU_LOAD@@
	},
@@MORE_FUNCTIONS@@
};"""

commonJsMenuBoolLoad = "		win.document.getElementById('@@EXTENSION_INTERNAL_NAME@@_' + number + '_@@MENU_ID@@').setAttribute('hidden', !prefs.getBoolPref('SubMenu@@MENU_ID@@'));\n"

commonJsMenuCharLoad = """
		var custom = prefs.getCharPref('CustomPage@@CUSTOM_PAGE_ID@@');
		var customId = '@@EXTENSION_INTERNAL_NAME@@_' + number + '_c@@CUSTOM_PAGE_ID@@';
		if (custom == '')
			win.document.getElementById(customId).setAttribute('hidden', true);
		else
			win.document.getElementById(customId).setAttribute('hidden', false);
"""

commonJsShowLogo = """
		if (prefs.getBoolPref('ShowLogo'))
			class += ' @@EXTENSION_INTERNAL_NAME@@-l';
"""

commonJsPersPage = """
	customPage@@CUSTOM_PAGE_ID@@: function(event) {
		var prefs = this.getPrefs();
		var myhome = prefs.getCharPref('@@CUSTOM_PAGE_PREF@@');
		var url = "@@CUSTOM_PAGE_BASE_URL@@" + myhome;
		@@EXTENSION_INTERNAL_NAME@@Url.openClearLink(event, url);
	},"""

commonJsMailArchive = """
	mailArchive@@MAIL_ARCHIVE_ID@@: function(event, type) {
		var date = new Date();
		var month = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");
		var url = "@@MAIL_ARCHIVE_BASE_URL@@" + date.getFullYear() + "-" + month[date.getMonth()] + "/" + type + ".html";
		@@EXTENSION_INTERNAL_NAME@@Url.openClearLink(event, url);
	},"""

openJsMain = """
var @@EXTENSION_INTERNAL_NAME@@Url = {

	closePopup: function(event){
		var element = event.target.parentNode;

		while (element) {
			if (element.nodeName == "menupopup" )
				element.hidePopup();
			element = element.parentNode;
		}
	},

	getURL: function(url) {
		var win = Components.classes["@mozilla.org/appshell/window-mediator;1"].
		getService(Components.interfaces.nsIWindowMediator).
		getMostRecentWindow("navigator:browser");
		return win.document.getElementById("@@EXTENSION_INTERNAL_NAME@@-bundle").getString(url);
	},

	openLink: function(event, url) {
		if (event && event.button != 0)
			getBrowser().addTab(unescape(this.getURL(url)));
		else
			loadURI(unescape(this.getURL(url)));
	},

	openClearLink: function(event, url) {
		if (event && event.button != 0)
			getBrowser().addTab(unescape(url));
		else
			loadURI(unescape(url));
	},
@@MORE_FUNCTIONS@@
}"""

openJsGetForm = """
	getSearchForm@@GET_FORM_ID@@: function(event, text) {
		var find = window._content.document.getSelection();
		var search = prompt(text, find);
		if (search != null) {
			var url = "@@GET_FORM_BASE_URL@@" + search;
			this.openClearLink(event, url);
		}
	},"""

prefsJsMain = """
var @@EXTENSION_INTERNAL_NAME@@Options = {

	getPrefs: function() {
		return Components.classes["@mozilla.org/preferences-service;1"].
		getService(Components.interfaces.nsIPrefService).
		getBranch("extensions.@@EXTENSION_INTERNAL_NAME@@.");
	},

	onDialogLoad: function() {
		var prefs = this.getPrefs();

		document.getElementById('TitleMenu').checked = prefs.getBoolPref('TitleMenu');
		document.getElementById('ToolsMenu').checked = prefs.getBoolPref('ToolsMenu');
		document.getElementById('ContextMenu').checked = prefs.getBoolPref('ContextMenu');
		document.getElementById('Options').checked = prefs.getBoolPref('Options');
@@PREFS_LOAD_PREFS@@
	},

	onDialogAccept: function() {
		var prefs = this.getPrefs();
		
		prefs.setBoolPref('TitleMenu',document.getElementById('TitleMenu').checked);
		prefs.setBoolPref('ToolsMenu',document.getElementById('ToolsMenu').checked);
		prefs.setBoolPref('ContextMenu',document.getElementById('ContextMenu').checked);
		prefs.setBoolPref('Options',document.getElementById('Options').checked);
@@PREFS_SAVE_PREFS@@
	},
};"""

prefsJsBoolLoad = """		document.getElementById('@@PREFS_MENU_ID@@').checked = prefs.getBoolPref('@@PREFS_MENU_ID@@');\n"""
prefsJsBoolSave = """		prefs.setBoolPref('@@PREFS_MENU_ID@@',document.getElementById('@@PREFS_MENU_ID@@').checked);\n"""

prefsJsCharLoad = """		document.getElementById('@@PREFS_MENU_ID@@').value = prefs.getCharPref('@@PREFS_MENU_ID@@');\n"""
prefsJsCharSave = """		prefs.setCharPref('@@PREFS_MENU_ID@@',document.getElementById('@@PREFS_MENU_ID@@').value);\n"""

debianDiffChanges = {'@@CONTROL_LENGHT@@':'debControlLenght', '@@CHANGELOG_LENGHT@@':'debChangelogLenght', '@@COPYRIGHT_LENGHT@@':'debCopyrightLenght', '@@DEB_CHANGELOG@@':'debianChangelog', '@@DATE_TIME@@':'debDateTime', '@@DIR_NAME@@':'dirName', '@@EXT_AUTHOR@@':'debExtAuthor', '@@EXTENSION_BZR_BRANCH@@':'bzrBranch', '@@EXTENSION_DESC@@':'debExtDesc', '@@EXTENSION_HOMEPAGE@@':'homepageURL', '@@EXTENSION_INTERNAL_NAME@@':'internalName', '@@EXTENSION_SHORT_DESC@@':'shortDesc', '@@EXT_ICON_LICENSE@@':'debIconLicense', '@@MANTAINER@@':'maintainer', '@@ORIG_MANTAINER@@':'origMaintainer', '@@WATCH_DIR@@':'watchDir', '@@YEAR@@':'year', '@@PACKAGE_NAME@@':'packageName'}

debianDiffMain = """--- @@DIR_NAME@@.orig/debian/control
+++ @@DIR_NAME@@/debian/control
@@ -0,0 +1,@@CONTROL_LENGHT@@ @@
+Source: @@PACKAGE_NAME@@
+Section: web
+Priority: optional
+Maintainer: @@MANTAINER@@
+XSBC-Original-Maintainer: @@ORIG_MANTAINER@@
+Build-Depends: debhelper (>= 5), cdbs
+Build-Depends-Indep: mozilla-devscripts (>= 0.5~), ant
+Homepage: @@EXTENSION_HOMEPAGE@@
+Vcs-Bzr: @@EXTENSION_BZR_BRANCH@@
+Standards-Version: 3.8.0
+
+Package: firefox-@@PACKAGE_NAME@@
+Architecture: all
+Depends: firefox | firefox-3.0 | firefox-2
+Description: @@EXTENSION_SHORT_DESC@@
@@EXTENSION_DESC@@
--- @@DIR_NAME@@.orig/debian/rules
+++ @@DIR_NAME@@/debian/rules
@@ -0,0 +1,8 @@
+#!/usr/bin/make -f
+
+MOZ_EXTENSION_PKG := firefox-@@PACKAGE_NAME@@
+MOZ_XPI_BUILD_COMMAND := ant createxpi
+
+include /usr/share/cdbs/1/rules/debhelper.mk
+include /usr/share/mozilla-devscripts/xpi.mk
+
--- @@DIR_NAME@@.orig/debian/watch
+++ @@DIR_NAME@@/debian/watch
@@ -0,0 +1,3 @@
+version=3
+@@WATCH_DIR@@/@@EXTENSION_INTERNAL_NAME@@_(.*)\.orig\.tar\.gz
+
--- @@DIR_NAME@@.orig/debian/changelog
+++ @@DIR_NAME@@/debian/changelog
@@ -0,0 +1,@@CHANGELOG_LENGHT@@ @@
@@DEB_CHANGELOG@@
--- @@DIR_NAME@@.orig/debian/compat
+++ @@DIR_NAME@@/debian/compat
@@ -0,0 +1 @@
+5
--- @@DIR_NAME@@.orig/debian/copyright
+++ @@DIR_NAME@@/debian/copyright
@@ -0,0 +1,@@COPYRIGHT_LENGHT@@ @@
+This package was debianized by
+@@ORIG_MANTAINER@@ on
+@@DATE_TIME@@.
+
+It was downloaded from @@WATCH_DIR@@/
+
+Upstream Author: @@EXT_AUTHOR@@
+
+Copyright: @@YEAR@@, @@EXT_AUTHOR@@
+
+License:
+
+    This package is free software; you can redistribute it and/or modify
+    it under the terms of the GNU General Public License as published by
+    the Free Software Foundation; either version 2 of the License, or
+    (at your option) any later version.
+    
+    This package is distributed in the hope that it will be useful,
+    but WITHOUT ANY WARRANTY; without even the implied warranty of
+    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
+    GNU General Public License for more details.
+    
+    You should have received a copy of the GNU General Public License
+    along with this package; if not, write to the Free Software
+    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
+
+Full license is distributed in upstream tarball through this file:
+chrome/content/@@EXTENSION_INTERNAL_NAME@@/GPLv3Licence.txt
+
+On Debian systems, the complete text of the GNU General
+Public License can be found in `/usr/share/common-licenses/GPL'.
@@EXT_ICON_LICENSE@@
+The Debian packaging is (C) @@YEAR@@, @@ORIG_MANTAINER@@ and
+is licensed under the GPL, see above.
+
"""

if __name__ == '__main__':
	sys.exit(__doc__)
