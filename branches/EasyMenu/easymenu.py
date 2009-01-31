#===================================================================#
# Program: Easy Menu v. 1.0.3
# Short description: a multi-browser automagic extension builder
# Online resources: http://easymenu.googlepages.com/
#                   https://launchpad.net/easymenu
# File: easymenu.py
# Date: 2008/08/27
# Last modified: 2008/10/12
# Copyright (c) 2008 Riccardo Coccioli (Volans) <easymenu@gmail.com>
# License: GNU General Public License version 3
# Full license notice: ./lib/LICENSE
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

try:
	import sys
	# Hack for Ubuntu Hardy see LP bug: 199014
	sys.path.append('/usr/lib/python%s/site-packages/oldxml' % sys.version[:3])

	import lib.menu_generator
except ImportError, detail:
	sys.exit(' ERROR - MODULE NOT FOUND: ' + str(detail) + '\n -- EXIT --')

if __name__ == '__main__':
	print '\n -- EASY MENU v1.0.3 --\n'
	try:
		lib.menu_generator.main(sys.argv[1:])
	except (KeyboardInterrupt):
		sys.exit(' ERROR - Program interrupted by the user\n -- EXIT --')
