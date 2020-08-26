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


def warning():
	debug('''
[*] WARNING: DON'T LET THE LAPTOP FALL ASLEEP!!! Move mouse, etc. Breaking the flashing process can brick the module!

[!] Make sure that:
	- The car is connected to an external power source 
	- Laptop is sufficiently charged / plugged to an external power source
	- Laptop will not fall asleep/hibernate/etc during this process (power management settings on the host machine) 
	- You have the internet connection

[?] Do you wish to continue? (y/N) ''', end='')
	if input().lower() != 'y':
		return False

	debug('''
[>] Great! Please follow the steps below:
	1. Connect your Particle device to the computer's USB port but DO NOT plug it to the OBD port just yet
	2. Connect it to this Virtual Machine (select Virtual Machine -> USB -> Connect Particle from the menu)
	3. If you got your Carloop preflashed from DaftRacing it should be fading Gray by now.

[?] Hit return when ready... ''', end='')
	input()

	return True


def choose_calibration():
	calibrations = [
		[ 'Stock', 'G1F7-14C366-AL.vbf'],
		[ 'DaftRDU T5 (+12%, 1700Nm limit)', 'G1F7-14C366-AL-DAFT-T5.vbf' ],
		[ 'DaftRDU T11 [EXPERIMENTAL] (+25%, SWVEC OFF, 1700Nm limit)', 'G1F7-14C366-AL-DAFT-T11.vbf' ],
		[ 'DaftRDU T13 [EXPERIMENTAL] (+25%, SWVEC ON, 1700Nm limit)', 'G1F7-14C366-AL-DAFT-T13.vbf' ]
	]
	debug('\n[ ] Which calibration to flash?')
	i = 0
	for c in calibrations:
		debug("\t[{}] {}".format(i, c[0]))
		i += 1
	debug("[?] Type 0-{} and hit return... ".format(i-1), end='')
	c = input()

	datasets = [
		[ 'Stock', 'G1F7-14C367-AL.vbf' ],
		[ 'DaftRDU DS1 (170C RDU Oil Temp Limit)', 'G1F7-14C367-AL-DAFT-DS1.vbf' ],
		[ 'DaftRDU DS3 (FWD in Normal DM + 170C)', 'G1F7-14C367-AL-DAFT-DS3.vbf' ]
	]
	debug('\n[ ] Which parameter set to flash?')
	i = 0
	for d in datasets:
		debug("\t[{}] {}".format(i, d[0]))
		i += 1
	debug("[?] Type 0-{} and hit return... ".format(i-1), end='')
	d = input()

	try:
		r = [calibrations[int(c)], datasets[int(d)]]
	except ValueError:
		debug('[!] Invalid calibration / parameters selected')
		return None
	except IndexError:
		debug('[!] Invalid calibration / parameters selected')
		return None

	return r


def main():
	if not warning():
		return

	if not carloop_init("HSCAN"):
		return

	v = choose_calibration()
	if not v:
		return
	
	debug('''\n[>] All set, we are good to go!
	1. Connect Carloop device to the OBD diagnostic port
	2. Turn ON the ignition but do NOT start the engine
	3. Hit return when ready to flash {} / {}'''.format(v[0][0], v[1][0]))
	input()

	try:
		flasher = Vbflasher(can_interface = 'slcan0', sbl_path='vbf/G1F7-14C368-AA.vbf', exe_path='vbf/{}'.format(v[0][1]), \
			data_path='vbf/{}'.format(v[1][1]))
	except OSError as e:
		enum = e.args[0]
		if enum == 19:
			debug('[!] Unable to open slcan0 device')
		return

	debug("\n[+] Successfully opened slcan0")

	flasher.start()
	flasher.flash()
	flasher.ver()

	debug('[+] Flashing completed!\n')

	debug('''[>] Final steps:
	1. Turn the ignition OFF
	2. You can now safely disconnect Carloop
	3. Start the engine
''')


if __name__ == '__main__':
	main()
	input()
