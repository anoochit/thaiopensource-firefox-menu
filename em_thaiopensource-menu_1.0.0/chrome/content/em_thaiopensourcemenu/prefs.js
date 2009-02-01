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


var em_thaiopensourcemenuOptions = {

	getPrefs: function() {
		return Components.classes["@mozilla.org/preferences-service;1"].
		getService(Components.interfaces.nsIPrefService).
		getBranch("extensions.em_thaiopensourcemenu.");
	},

	onDialogLoad: function() {
		var prefs = this.getPrefs();

		document.getElementById('TitleMenu').checked = prefs.getBoolPref('TitleMenu');
		document.getElementById('ToolsMenu').checked = prefs.getBoolPref('ToolsMenu');
		document.getElementById('ContextMenu').checked = prefs.getBoolPref('ContextMenu');
		document.getElementById('Options').checked = prefs.getBoolPref('Options');
		document.getElementById('ShowLogo').checked = prefs.getBoolPref('ShowLogo');

	},

	onDialogAccept: function() {
		var prefs = this.getPrefs();
		
		prefs.setBoolPref('TitleMenu',document.getElementById('TitleMenu').checked);
		prefs.setBoolPref('ToolsMenu',document.getElementById('ToolsMenu').checked);
		prefs.setBoolPref('ContextMenu',document.getElementById('ContextMenu').checked);
		prefs.setBoolPref('Options',document.getElementById('Options').checked);
		prefs.setBoolPref('ShowLogo',document.getElementById('ShowLogo').checked);

	},
};