# ####################################################################
# gofed - set of tools to automize packaging of golang devel codes
# Copyright (C) 2014  Jan Chaloupka, jchaloup@redhat.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ####################################################################

import os
import optparse
from modules.GoSymbols import getGoDirs
from modules.GoSymbols import getSymbolsForImportPaths

def getSubdirs(directory):
	return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]

if __name__ == "__main__":

	parser = optparse.OptionParser("%prog [-p] [-d] [-t] [directory]")

	parser.add_option_group( optparse.OptionGroup(parser, "directory", "Directory to inspect. If empty, current directory is used.") )

	parser.add_option(
	    "", "-p", "--provides", dest="provides", action = "store_true", default = False,
	    help = "Display all directories with *.go files"
	)

	parser.add_option(
	    "", "-s", "--spec", dest="spec", action="store_true", default = "",
	    help = "If set with -p options, print list of provided paths in spec file format."
	)

	parser.add_option(
            "", "-d", "--dirs", dest="dirs", action = "store_true", default = False,
            help = "Display all direct directories"
        )

	parser.add_option(
	    "", "-t", "--test", dest="test", action = "store_true", default = False,
	    help = "Display all directories containing *.go test files"
	)

	options, args = parser.parse_args()

	path = "."
	if len(args):
		path = args[0]

	if options.provides:
		err, ip, _, _ = getSymbolsForImportPaths(path)
		if err != "":
			print err
			exit(1)

		ips = []
		for pkg in ip:
			ips.append(ip[pkg])

		for ip in sorted(ips):
			if options.spec != "":
				if ip != ".":
					print "Provides: golang(%%{import_path}/%s) = %%{version}-%%{release}" % (ip)
				else:
					print "Provides: golang(%{import_path}) = %{version}-%{release}"
			else:
				print ip

	elif options.test:
		sdirs = sorted(getGoDirs(path, test = True))
		for dir in sdirs:
			print dir
	elif options.dirs:
		sdirs = sorted(getSubdirs(path))
		for dir in sdirs:
			print dir
	else:
		print "Usage: prog [-p] [-d] [-t] [directory]"
