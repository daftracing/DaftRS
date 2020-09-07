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

import serial
import glob
from time import sleep

from helpers.misc import *


def particle_reset():
	wait_for_usb()
	output = run("particle usb reset", shell=True)
	sleep(2)
	if output.strip()[-5:] == 'Done.':
		return True
	return False


def particle_dfu():
	wait_for_particle()
	output = run("particle usb dfu", timeout=10, shell=True)
	sleep(5)
	return True

def particle_flash(model):
	wait_for_particle()

	name = {'0a': 'Electron', '06': 'Photon'}

	output = run("particle flash --usb firmware/SoftStick_{}.bin".format(name[model]), shell=True)
	sleep(1)
	if not "!!!" in output:
		return True
	return False	


def particle_update():
	wait_for_usb(dfu=True)
	sleep(1)

	while True:
		output = run("particle update", shell=True)
		if not "!!!" in output:
			return True
		debug('.', end='')
		sleep(3)

def wait_for_particle():
	output = run("particle usb list --ids-only | grep -i -v ERROR", shell=True)

	if output:
		return

	debug("\n[ ] Please reconnect Particle to this VM... ", end="")
	while not output:
		output = run("particle usb list --ids-only | grep -i -v ERROR", shell=True)

	debug('OK\r[+')


def wait_for_usb(dfu=False):
	if dfu:
		suffix = 'd0'
	else:
		suffix = 'c0'

	output = run("lsusb | grep 2b04:{}".format(suffix), shell=True)
	if output:
		return

	if(dfu):
		debug("\n[ ] Please make sure you enabled DFU mode (blinking orange) and reconnect Particle to this VM... ", end='')
	else:
		debug("\n[ ] Please reconnect Particle to this VM... ", end='')

	while not output:
		output = run("lsusb | grep 2b04:{}".format(suffix), shell=True)
		sleep(1)

	debug('OK\r[+')


def check_usb():
	debug('[?] Checking USB connection... ', end='')

	output = run("lsusb | grep 2b04", shell=True)
	if output:
		product = output.split(':')[2].split(' ')[0].strip()
		model = product[2:]
		debug('OK\r[+')
		return model
	else:
		debug("\n[!] No device detected. Make sure it's connected to this Virtual Machine and try again.")

	return False


def	manualfw_redbear():
	debug('\n[?] Do you wish to update your RedBear and flash DaftRacing firmware? (y/N)')
	if input().lower() != 'y':
		return False

	debug('''[>] Put your RedBear Duo into DFU mode:
\t1) Press and hold both the RESET/RST and MODE/SETUP buttons simultaneously.
\t2) Release only the RESET/RST button while continuing to hold the MODE/SETUP button.
\t3) Release the MODE/SETUP button once the device begins to blink yellow.
\t4) Reconnect RedBear Duo to this VM
\t5) Press return''');
	input()

	sleep(5)
	wait_for_usb(dfu=True)
	
	debug('\n[ ] Updating RedBear... ', end='')
	run('sudo dfu-util -d 2b04:d058 -a 0 -s 0x8020000 -D ./firmware/3rdparty/duo-system-part1-v0.3.3.bin 2>&1', shell=True)
	run('sudo dfu-util -d 2b04:d058 -a 0 -s 0x8040000 -D ./firmware/3rdparty/duo-system-part2-v0.3.3.bin 2>&1', shell=True)
	run('sudo dfu-util -d 2b04:d058 -a 2 -s 0x180000 -D ./firmware/3rdparty/duo-wifi-r2.bin 2>&1', shell=True)
	debug('OK\r[+')

	debug('\n[ ] Flashing the firmware... ', end='')
	run('sudo dfu-util -d 2b04:d058 -a 0 -s 0x080C0000 -D ./firmware/SoftStick_RedBear.bin 2>&1', shell=True)
	debug('OK\r[+')

	debug('[>] Please reset RedBear, reconnect and hit return')
	input()
	wait_for_usb()

	return True


def manualfw_particle(model):
	debug('\n[*] Flashing DaftRacing firmware...')

	updated = False
	while not updated:
		debug('''[>] Put your Particle into DFU mode:
\t1) Press and hold both the RESET/RST and MODE/SETUP buttons simultaneously.
\t2) Release only the RESET/RST button while continuing to hold the MODE/SETUP button.
\t3) Release the MODE/SETUP button once the device begins to blink yellow.
\t4) Reconnect Particle DFU to this VM
\t5) Press return''');
		input()
	
		sleep(5)
		wait_for_usb(dfu=True)
		debug('\n[ ] Updating Particle (needs internet connection!)...', end='')
		if not particle_update():
			debug('Failed to connect!\r[-')
		else:
			updated = True

	debug(' OK\r[+')

	sleep(5)	
	wait_for_particle()
	debug('\n[ ] Going back to DFU... ', end='')
	if not particle_dfu():
		debug('Failed!\r[!')
		return False
	debug('OK\r[+')

	sleep(5)
	wait_for_particle()
	debug('\n[ ] Flashing the firmware... ', end='')
	if not particle_flash(model):
		debug('Failed!\r[!')
		return False
	debug('OK\r[+')

	sleep(3)
	wait_for_particle()
	return True


def manualfw(model):
	if model == '06' or model == '0a':
		return manualfw_particle(model)
	if model == '58':
		return manualfw_redbear()

	debug('\nHint: Register your device and flash firmware/SoftStick.ino using Particle Web IDE (https://build.particle.io/build)')
	return False


def check_firmware(model):
	sleep(5)
	debug('\n[?] Looking for DaftRacing multimode firmware... ')

	if model == '06' or model == '0a':
		wait_for_particle()
		perror = run('particle usb list -v --ids-only | grep -i error', shell=True)
		if perror:
			debug('[!] Device not recognized...')
			return False
	else:
		wait_for_usb()


	debug('\t[ ] Opening serial connection... ', end='')

	lastacm = None
	for a in glob.glob('/dev/ttyACM*'):
		lastacm = a
	if not lastacm:
		return False

	ser = serial.Serial(lastacm, 9600, timeout=5)
	if not ser:
		return False

	debug('OK\r\t[+')

	debug('\t[?] Checking firmware version... ', end='')
	ser.write(b'v\r')
	firmware = ser.readline()
	ser.close()
	if not firmware or not b'multimode' in firmware:
		debug('\r\t[-] No DaftRacing firmware found on this Particle device...')
		return False
	debug('\r\t[+] Firmware: {}'.format(firmware.decode("utf-8")))

	return True


def iface(speed):
	s = 0
	if speed == "MSCAN":
		s = 4
	if speed == "HSCAN":
		s = 6
	if not s:
		return False

	debug('[ ] Bringing CAN interface up (Particle should start fading green)... ', end='')
	run('sudo slcand -s{} -f -o -c /dev/ttyACM*'.format(s), shell=True)
	sleep(3)
	run('sudo ifconfig slcan0 up', shell=True)
	run('sudo ip link set txqueue 1000 dev slcan0', shell=True)
	debug('OK\r[+')

	return True


def carloop_init(speed):
	run('sudo killall slcand > /dev/null 2>&1', shell=True)

	wait_for_usb()
	model = check_usb()
	if not model:
		return False

	if not check_firmware(model):
		if manualfw(model):
			if not check_firmware(model):
				debug("\n[!] Please manually install Daftracing firmware from firmware/SoftStick.ino")
				return False
		else:
			return False

	if not iface(speed):
		return False

	return True

def carloop_close():
	debug('[ ] Closing CAN interface... ', end='')
	run('sudo killall slcand', shell=True)
	debug('OK\r[+\n[ ] Carloop reset... ', end='')
	run('particle usb reset', shell=True)
	debug('OK\r[+\n')
