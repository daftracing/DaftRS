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
[*] WARNING: Breaking the flashing process WILL brick the ABS module!
[*] LEGAL: Please respect all the EULAs, IP rights, etc. Flash only the calibrations you are entitled to use!

[!] Make sure that:
	- The car is connected to an external power source 
	- Laptop is sufficiently charged / plugged to an external power source
	- Laptop will not fall asleep/hibernate/etc during this process (power management settings on the host machine) 
	- You have internet connection 
	- You are actually flashing Ford Focus RS Mk3 with a calibration that you are entitled to use

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


def check_calibration():
	debug('\n[?] Checking calibration files...')
	while not os.path.isfile('3rdparty/G1FC-14C036-BA.tar.bz2'):
		debug('\t[-] No calibration files found. Try to download? (y/N) ', end='')
		if input().lower() == 'y':
			run('megadl --path=3rdparty https://mega.nz/#!uMUn0Y7K!QE-TG9zWQJVYcAIJFxwWbDPqnQ2VqTA9DYKZn-GV3o4', shell=True, stdout=None)
		else:
			debug('\t    Download G1FC-14C036-BA.tar.bz2 (https://mega.nz/#!uMUn0Y7K!QE-TG9zWQJVYcAIJFxwWbDPqnQ2VqTA9DYKZn-GV3o4)')
			debug('\t    and copy to "3rdparty" directory. Hit return when done.', end='')
			input()

	debug('\t[+] Extracting...')
	run('tar jxf 3rdparty/G1FC-14C036-BA.tar.bz2 -C /tmp', shell=True)
	if os.path.isfile('/tmp/G1FC-14C036-BA.vbf') and os.path.isfile('/tmp/G1FC-14C381-BA.vbf') \
		and os.path.isfile('/tmp/E3B1-14C039-AA.vbf'):
		debug('[+] OK\n')
		return True
	else:
		debug('[!] Broken archive! Aborting...')
		return False


def main():
	if not warning():
		return

	if not check_calibration():
		return

	carloop_init("HSCAN")

	debug('''\n[>] All set, we are good to go!
	1. Connect Carloop device to the OBD diagnostic port
	2. Turn ON the ignition but do NOT start the engine
	3. Hit return when ready''')
	input()

	try:
		flasher = Vbflasher(can_interface = 'slcan0', sbl_path='/tmp/E3B1-14C039-AA.vbf', exe_path='/tmp/G1FC-14C036-BA.vbf', \
			data_path='/tmp/G1FC-14C381-BA.vbf')
	except OSError as e:
		enum = e.args[0]
		if enum == 19:
			debug('[!] Unable to open slcan0 device')
		return
	debug("\n[+] Successfully opened slcan0")

	flasher.start()
	flasher.flash()
	flasher.ver()

	carloop_close()

	debug('''[>] Final steps:
	1. You can now safely disconnect USB cable from Particle
	2. Turn the ignition OFF, then ON and start the car
	3. Particle will fade Gray, it's ready but will NOT drift
	4. Disable ESC (press and hold until OFF)
	5. Particle should turn Red. Ready to drift!
	6. Try it out by gently pulling the handbrake while rolling :)
	7. Have fun!

[!] Note: The device will be put in deep sleep mode when the engine is off and wake up in less than a minute when started.
''')


if __name__ == '__main__':
	main()
	input()
