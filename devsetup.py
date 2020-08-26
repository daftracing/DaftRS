#!/usr/bin/env python3

"""
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""


import sys
sys.path.append('./tools')

from tools.vbflasher import Vbflasher
from helpers.carloop import *


def main():
	if len(sys.argv) < 2:
		speed = "HSCAN"
	else:
		speed = sys.argv[1]

	debug("[>] Setting up Carloop to work with {}".format(speed))
	return carloop_init(speed)


if __name__ == '__main__':
	main()
