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


window.addEventListener("load", em_thaiopensourcemenuLoad, false);

function em_thaiopensourcemenuLoad() {
	gBrowser.addProgressListener(em_thaiopensourcemenuProgress);
	em_thaiopensourcemenuCommon.onLoad();
}

window.addEventListener("unload", em_thaiopensourcemenuUnload, false);

function em_thaiopensourcemenuUnload() {
	gBrowser.removeProgressListener(em_thaiopensourcemenuProgress);
}

function em_thaiopensourcemenuCheckStatus() {
	var a = em_thaiopensourcemenuProgress.webprog;
	if ((a && !a.isLoadingDocument) || !a)
		em_thaiopensourcemenuCommon.onLoad();
}

var em_thaiopensourcemenuProgress = {
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
		window.setTimeout(em_thaiopensourcemenuCheckStatus,200);
	},

	onProgressChange: function(a,b,c,d,e,f) { },
	onSecurityChange: function(a,b,c) { },
	onStateChange: function(a,b,c,d) {
		if ((a && !a.isLoadingDocument) || !a) {
			em_thaiopensourcemenuCommon.onLoad();
		}
	},
	onStatusChange: function(a,b,c,d) { }
};

var em_thaiopensourcemenuCommon = {

	getPrefs: function() {
		return Components.classes["@mozilla.org/preferences-service;1"].
		getService(Components.interfaces.nsIPrefService).
		getBranch("extensions.em_thaiopensourcemenu.");
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

		if (prefs.getBoolPref('ShowLogo'))
			class += ' em_thaiopensourcemenu-l';

		win.document.getElementById('em_thaiopensourcemenuTitleMenu').setAttribute('hidden', !prefs.getBoolPref('TitleMenu'));
		win.document.getElementById('em_thaiopensourcemenuTitleMenu').setAttribute('class', class);
		win.document.getElementById('em_thaiopensourcemenuToolsMenu').setAttribute('hidden', !prefs.getBoolPref('ToolsMenu'));
		win.document.getElementById('em_thaiopensourcemenuToolsMenu').setAttribute('class', class);
		win.document.getElementById('em_thaiopensourcemenuContextMenu').setAttribute('hidden', !prefs.getBoolPref('ContextMenu'));
		win.document.getElementById('em_thaiopensourcemenuContextMenu').setAttribute('class', class);
	},

	onMenuLoad: function(number) {
		var prefs = this.getPrefs();
		var win = this.getMainWin();
		win.document.getElementById('em_thaiopensourcemenuSepOptions' + number).setAttribute('hidden', !prefs.getBoolPref('Options'));
		win.document.getElementById('em_thaiopensourcemenuOptions' + number).setAttribute('hidden', !prefs.getBoolPref('Options'));

	},

};