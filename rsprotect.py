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

from time import sleep
import hashlib

from tools.ford.uds import Ecu
from tools.vbflasher import Vbflasher
from helpers.misc import *
from helpers.carloop import *



def warning():
	debug('''
[*] WARNING: Breaking the flashing process can brick the KVM module!

[!] Make sure that:
	- The car is connected to an external power source 
	- Carloop/CAN inteface is NOT conntected to the OBD port just yet
	- Laptop is sufficiently charged / plugged to an external power source
	- Laptop will not fall asleep/hibernate/etc during this process (power management settings on the host machine) 

[?] Do you wish to continue? (y/N) ''', end='')
	if input().lower() != 'y':
		return False

	return True


def protect(dev):
	p = 1
	p2 = p+1
	while p != p2:
		p = input("\n[?] New KVM password: ")
		p2 = input("[?] Confirm password: ")
	px = hashlib.sha1(p.encode('ASCII')).digest()[:4]
	pinstr = ''.join(['{:02x}'.format(a) for a in px])

	print("[>] Please save the password and the recovery PIN: {}. Hit return to continue.".format(' '.join(['0x{:02x}'.format(a) for a in px])))
	input()

	debug('[?] Checking calibration files... ')

	for f in ['F1FT-14C107-AA', 'F1FT-14C104-AN-RSPROT', 'F1FT-14C105-AH']:
		print("\t{}: ".format(f), end="")
		if not os.path.isfile('./vbf/{}.vbf'.format(f)):
			debug('Not found\n[!] Missing calibration files. Please run build.sh script in the vbf folder.')
			return
		run('cp ./vbf/{}.vbf /tmp/'.format(f), shell=True)
		print("OK")

	debug("\n[>] Preparing custom calibration binary")
	debug("\tExtracting binaries... ", end="")
	run('./tools/vbfextract.py /tmp/F1FT-14C104-AN-RSPROT.vbf', shell=True)
	debug("OK")
	debug("\tPatching... ", end="")
	with open('/tmp/F1FT-14C104-AN-RSPROT.vbf.0x00010010', 'rb') as ori:
		data = bytearray(ori.read())
		px1 = (px[0] << 8) + px[1]
		px2 = (px[2] << 8) + px[3]
		if px2 > 0x7fff:
			px1 = (px1 + 1) & 0xffff

		data[0x4eaac] = px1 >> 8
		data[0x4eaad] = px1 & 0xff
		data[0x4eab2] = px2 >> 8
		data[0x4eab3] = px2 & 0xff

		with open('/tmp/F1FT-14C104-AN-RSPROT-{}.vbf.0x00010010'.format(pinstr), 'wb') as cust:
			cust.write(data)
	debug("OK\n")

	debug(run('''./tools/vbfmake.py --sw F1FT-14C104-AN-RSPROT --type EXE --can CAN_MS --ecu 0x731 --erase-memory 0x00010000:0x00070000 \
	 --fix-checksum --out /tmp/F1FT-14C104-AN-RSPROT-{}.vbf 0x00010010:/tmp/F1FT-14C104-AN-RSPROT-{}.vbf.0x00010010 \
	 0x0007eff8:/tmp/F1FT-14C104-AN-RSPROT.vbf.0x0007eff8'''.format(pinstr, pinstr), shell=True))

	input("[?] Ready to flash. Connect Carloop / CAN interface to the OBD port and hit return to continue!")

	try:
		flasher = Vbflasher(can_interface=dev, sbl_path='./vbf/F1FT-14C107-AA.vbf', exe_path='/tmp/F1FT-14C104-AN-RSPROT-{}.vbf'.format(pinstr), \
			data_path='./vbf/F1FT-14C105-AH.vbf')
	except OSError as e:
		enum = e.args[0]
		if enum == 19:
			debug('\n[!] Unable to open {} device'.format(dev))
		return

	flasher.start()
	flasher.flash()
	flasher.ver()

	ecu = Ecu(can_interface=dev, ecuid=0x731)

	debug("\n[?] Testing PATS access... ")
	ecu.UDSDiagnosticSessionControl(0x03)
	sleep(1)
	r,m = ecu.unlock(0x11)
	if r:
		debug("[!] Not protected. Something went wrong...")
		return
	debug("[+] Failed, module protected!")

	debug("\n[?] Testing reprogramming access... ")
	ecu.UDSDiagnosticSessionControl(0x02)
	sleep(1)
	r,m = ecu.unlock(0x1)
	if r:
		debug("[!] Not protected. Something went wrong...")
		return
	debug("[+] Failed, Module protected!")

	debug("\n[+] RSProtect successfully installed!")
	

def unprotect(dev):
	input("\n[?] Connect Carloop / CAN interface to the OBD port and hit return to continue!")

	p = input("\n[?] KVM password: ")
	px = hashlib.sha1(p.encode('ASCII')).digest()[:4]

	try:
		ecu = Ecu(can_interface=dev, ecuid=0x731)
		debug("\n[+] Successfully opened {}".format(dev))

		debug("\n[ ] Sending PIN ({}) to unprotect the KVM... ".format(' '.join([ '0x{:02x}'.format(a) for a in px ])), end="")
		ecu.send(bytearray([0xff, 0xff, 0xff, px[0], px[1], px[2], px[3], 0xff]))
		ecu.recv()
		sleep(1)
		ecu.UDSTesterPresent()
		sleep(1)
		debug("OK\r[+")

		debug("\n[ ] Checking if it worked... ")
		ecu.UDSDiagnosticSessionControl(0x02)
		sleep(1)
		
		r,m = ecu.unlock(0x01)
		if not r:
			debug("[!] Nope... Wrong password?")
			return
		debug("[+] Module is unprotected for this session\n")

		debug("[>] Flashing the stock software...")
		flasher = Vbflasher(can_interface=dev, sbl_path='./vbf/F1FT-14C107-AA.vbf', exe_path='./vbf/F1FT-14C104-AN.vbf', \
			data_path='./vbf/F1FT-14C105-AH.vbf')
	except OSError as e:
		enum = e.args[0]
		if enum == 19:
			debug('\n[!] Unable to open {} device'.format(dev))
		return

	flasher.start()
	flasher.flash()
	flasher.ver()

	ecu = Ecu(can_interface=dev, ecuid=0x731)
	sw = ecu.getStrategy()
	if sw or not "RSPROT" in sw:
		debug('\n[>] KVM software is back to stock ({}). You may proceed with the PATS programming the usual way.'.format(sw))

def main():
	if not warning():
		return

	if len(sys.argv) < 2:
		carloop_init("MSCAN", minver=100)
		dev = "slcan0"
	else:
		dev = sys.argv[1]

	while True:
		op = input('\n[?] Protect or Unprotect the KVM module? [P/U]: ')
		if op.lower() == 'u':
			return unprotect(dev)
		if op.lower() == 'p':
			return protect(dev)


if __name__ == '__main__':
	main()
	input()
