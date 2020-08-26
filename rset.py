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

import argparse

from time import time, sleep
from tools.ford.uds import keygen, fixedbytes, Ecu


def debug(str, end="\n"):
	print(str, end=end)
	sys.stdout.flush()


def die(str):
	debug(str)
	sys.exit(-1)


def rdu_help():
	debug("""Rear Drive Unit settings

Available options:

  get		Check RDU status
  on		Set RDU on
  off		Set RDU off
""")


def rdu_get(ecu):
	status = "OFF"

	s = ecu.UDSReadDataByIdentifier([0xee, 0x0b])

	if s[0] == 0x01:
		status = "ON"

	debug("[?] RDU is currently {}".format(status))


def rdu_set(ecu, mode):
	rdu_get(ecu)

	debug("[+] Unlocking the ECU...")
	ecu.unlock(0x03)
	sleep(1)

	debug("[+] Sending data to 0x{:x}... ".format(ecu.ecuid), end="")
	if ecu.UDSWriteDataByIdentifier([0xee, 0x0b], [mode]):
		debug("OK")
		return rdu_get(ecu)
	else:
		debug("\n[-] Unable to write data...")

	
def rdu(args):
	ecuid = 0x703
	op = args.options

	ecu = Ecu(can_interface=args.can, ecuid=ecuid)
	debug("[+] Successfuly opened {} device".format(args.can))
	debug("[+] Sending TesterPresent to 0x{:x}... ".format(ecuid), end="")
	if ecu.UDSTesterPresent():
		debug("OK")
	else:
		die("\n[-] 0x{:x} did not send positive reposnse to our tester message... Aborting".format(ecuid))
	debug("[+] Starting diagnostic session 0x03... ".format(ecuid), end="")
	if 	ecu.UDSDiagnosticSessionControl(0x03):
		debug("OK")
	else:
		die("\n[-] Unable to start diagnostic session... Aborting".format(ecuid))
	sleep(0.5)


	if op[0] == "get":
		return rdu_get(ecu)
	if op[0] == "on":
		return rdu_set(ecu, 0x01)
	if op[0] == "off":
		return rdu_set(ecu, 0x00)

	return rdu_help()


def pdc_help():
	debug("""Enable/Disable Pull Drift Compensation

Available options:

  get		Check PDC status
  on		Set PDC on
  off		Set PDC off
""")


def pdc_get(ecu):
	status = "OFF"

	s = ecu.UDSReadDataByIdentifier([0xfd, 0x07])

	if s[0] == 0x01:
		status = "ON"

	debug("[?] PDC is currently {}".format(status))


def pdc_set(ecu, mode):
	pdc_get(ecu)

	debug("[+] Unlocking the ECU...")
	ecu.unlock(0x01)
	sleep(1)

	debug("[+] Sending data to 0x{:x}... ".format(ecu.ecuid), end="")
	if ecu.UDSWriteDataByIdentifier([0xfd, 0x07], [mode]):
		debug("OK")
		debug("[+] Resetting ECU... ", end="")
		if ecu.Reset(0x02):
			debug("OK")
			sleep(1)
			return pdc_get(ecu)
		else:
			debug("\n[-] Reset failed!")
			return
	else:
		debug("\n[-] Unable to write data...")

	
def pdc(args):
	ecuid = 0x730
	op = args.options

	ecu = Ecu(can_interface=args.can, ecuid=ecuid)
	debug("[+] Successfuly opened {} device".format(args.can))
	debug("[+] Sending TesterPresent to 0x{:x}... ".format(ecuid), end="")
	if ecu.UDSTesterPresent():
		debug("OK")
	else:
		die("\n[-] 0x{:x} did not send positive reposnse to our tester message... Aborting".format(ecuid))
	debug("[+] Starting diagnostic session 0x03... ".format(ecuid), end="")
	if 	ecu.UDSDiagnosticSessionControl(0x03):
		debug("OK")
	else:
		die("\n[-] Unable to start diagnostic session... Aborting".format(ecuid))
	sleep(0.5)

	if op[0] == "get":
		return pdc_get(ecu)
	if op[0] == "on":
		return pdc_set(ecu, 0x01)
	if op[0] == "off":
		return pdc_set(ecu, 0x00)

	return pdc_help()


def feng_help():
	debug("""
Enable/Disable Fake Engine Noise Generator

Available options:

  get		Check FENG status
  on		Set FENG on
  off		Set FENG off
""")


def feng_get(ecu):
	status = "OFF"

	s = ecu.UDSReadDataByIdentifier([0xee, 0x03])

	if s[0] == 0x01:
		status = "ON"

	debug("[?] FENG is currently {}".format(status))


def feng_on(ecu):
	feng_set(ecu, 0x01)


def feng_off(ecu):
	feng_set(ecu, 0x00)


def feng_set(ecu, mode):
	feng_get(ecu)

	debug("[+] Unlocking the ECU...")
	ecu.unlock(0x03)
	sleep(1)

	debug("[+] Sending data to 0x{:x}... ".format(ecu.ecuid), end="")
	if ecu.UDSWriteDataByIdentifier([0xee, 0x03], [mode]):
		debug("OK")
		sleep(1)
		return feng_get(ecu)
	else:
		debug("\n[-] Unable to write data...")


def feng(args):
	ecuid = 0x727
	op = args.options

	ecu = Ecu(can_interface=args.can, ecuid=ecuid)
	debug("[+] Successfuly opened {} device".format(args.can))
	debug("[+] Sending TesterPresent to 0x{:x}... ".format(ecuid), end="")
	if ecu.UDSTesterPresent():
		debug("OK")
	else:
		die("\n[-] 0x{:x} did not send positive reposnse to our tester message... Aborting".format(ecuid))
	debug("[+] Starting diagnostic session 0x03... ".format(ecuid), end="")
	if 	ecu.UDSDiagnosticSessionControl(0x03):
		debug("OK")
	else:
		die("\n[-] Unable to start diagnostic session... Aborting".format(ecuid))
	sleep(0.5)

	if op[0] == "get":
		return feng_get(ecu)
	if op[0] == "on":
		return feng_on(ecu)
	if op[0] == "off":
		return feng_off(ecu)

	return feng_help()	


def pcm_help():
	debug("""
PCM toolset

Available options:

  reset		Reset the PCM module
  forget	Make the PCM forget the learned data
  dump		Choose from below:
  	flash		Dump the whole flash contents, 4MiB from 0xc0000000
  	ram			Dump the RAM contents, 128kiB from 0xd0000000
  	region from	to
  memread	Read memory from the given address
  memwrite	Write value to the given address  
""")

def pcm_dumpram(ecu, op):
	return pcm_dumpmem(ecu, op, "RAM", 0xd0000000, 0xd0020000, 0x80)

def pcm_dumpflash(ecu, op):
	return pcm_dumpmem(ecu, op, "Flash", 0x80000000, 0x80400000, 0x80)

h = ['/', '-', '\\', '|']

def pcm_dumpmem(ecu, op, name, start, finish, block):
	if len(op) < 2 or not op[1]:
		debug("\n[-] Please provide the filename")
		return

	with open(op[1], "wb") as f:
		debug("\n[+] Dumping {} contents into {}".format(name, op[1]))

		i = 0
		for addr in range(start, finish, block):
			debug("\r\t0x{:08x} {} 0x{:08x} ... ".format(addr, h[i%4], finish), end="")
			mem = ecu.UDSReadMemoryByAddress(addr, block, aslen=0x24)
			if mem:
				f.write(mem)
			else:
				die("[!] Unable to read 0x{x} bytes from 0x{x}".format(block, addr))
			i += 1
			# sys.exit(0)

		debug("\n[+] Done.")


def pcm(args):
	ecuid = 0x7e0
	op = args.options

	ecu = Ecu(can_interface=args.can, ecuid=ecuid)
	debug("[+] Successfuly opened {} device".format(args.can))
	debug("[+] Sending TesterPresent to 0x{:x}... ".format(ecuid), end="")
	if ecu.UDSTesterPresent():
		debug("OK")
	else:
		die("\n[-] 0x{:x} did not send positive reposnse to our tester message... Aborting".format(ecuid))
	debug("[+] Starting diagnostic session 0x01... ".format(ecuid), end="")
	if 	ecu.UDSDiagnosticSessionControl(0x01):
		debug("OK")
	else:
		die("\n[-] Unable to start diagnostic session... Aborting".format(ecuid))
	sleep(0.5)

	if op[0] == "":
		return pcm_help(ecu)
	if op[0] == "dumpram":
		return pcm_dumpram(ecu, op)
	if op[0] == "dumpflash":
		return pcm_dumpflash(ecu, op)
	if op[0] == "dumppats":
		return pcm_dumpmem(ecu, op, "PATS", 0xd0006e80, 0xd0006f00, 0x80)

	return pcm_help()	


def main():
	parser = argparse.ArgumentParser(description="Set Focus RS specific options", epilog="If using MSCAN make sure to connect your can interface to Ford specific MSCAN OBD pins (3, 11) and to set the correct can bus speed (125k)!!!")
	parser.add_argument("--can", help="Can device to be used, can0 by default", default="can0")
	parser.add_argument("mode", type=str, help='PCM [HSCAN], RDU [HSCAN], PDC [HSCAN], FENG [MSCAN], PATS [HSCAN]')
	parser.add_argument("options", type=str, default=["help"], nargs="*", help="Mode specific options like help or get/set etc")

	args = parser.parse_args()

	if args.mode.lower() == "pcm":
		return pcm(args)
	if args.mode.lower() == "rdu":
		return rdu(args)
	if args.mode.lower() == "pdc":
		return pdc(args)
	if args.mode.lower() == "feng":
		return feng(args)
	if args.mode.lower() == "pats":
		return pats(args)

	debug("[-] Unknown mode {} ...".format(args.mode))


if __name__ == '__main__':
	main()
