/*
 This file was automagically generated on 2009-02-01 03:13:18 UTC
 by Easy Menu v. 1.0.3 ( http://easymenu.googlepages.com/ )
 and is part of 'Thai Open Source'.

 Thai Open Source is free software: you can redistribute it
 and/or modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation, either version 3 of
 the License, or (at your option) any later version.

 Thai Open Source is distributed in the hope that it will be
 useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Thai Open Source.
 If not, see http://www.gnu.org/licenses/.

 The copy of the GNU General Public License can be found here:
 chrome://em_thaiopensourcemenu/content/GPLv3License.txt
*/


var em_thaiopensourcemenuUrl = {

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
		return win.document.getElementById("em_thaiopensourcemenu-bundle").getString(url);
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

	getSearchForm1: function(event, text) {
		var find = window._content.document.getSelection();
		var search = prompt(text, find);
		if (search != null) {
			var url = "https://launchpad.net/+search?field.text=" + search;
			this.openClearLink(event, url);
		}
	},
}