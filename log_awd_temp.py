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
from datetime import datetime

from tools.vbflasher import Vbflasher
from helpers.carloop import *
from ford.uds import Ecu


def main():
	debug('\n[>] Connect Carloop but do NOT plug it to the OBD port just yet. Hit return when ready...')
	input()

	if not carloop_init("HSCAN"):
		return

	debug('\n[>] Start the car and then connect Carloop to the OBD port. Hit return when ready...')
	input()

	ecu = Ecu(can_interface="slcan0", ecuid=0x703)

	ids = [(0x1e, 0x3f), (0x1e, 0x8a), (0xd1, 0x1d), (0x1e, 0xcf), (0x1e, 0xd0)]
	v = dict()

	t = datetime.isoformat(datetime.now())
	path = './logs/awd-temp-{}.log'.format(t)
	with open(path, 'w') as f:
		debug("\r[>] Logging to {}. Press Ctrl-C to stop.".format(path))
		while True:
			for i in ids:
				j = list(i)
				d = ecu.UDSReadDataByIdentifier(j)
				v[i] = d
				t = datetime.isoformat(datetime.now())
				f.write('{} {} {}\n'.format(t, '[{}]'.format(', '.join(hex(x) for x in j)),
					'[{}]'.format(', '.join(hex(x) for x in d))))

			tmp = v[(0x1e, 0x3f)]
			ptuoil = float(tmp[1] + (tmp[0] << 8))/4
			tmp = v[(0x1e, 0xcf)]
			lclutch = float(tmp[1] + (tmp[0] << 8))/4
			tmp = v[(0x1e, 0xd0)]
			rclutch = float(tmp[1] + (tmp[0] << 8))/4

			rduoil = v[(0x1e, 0x8a)][0] - 40
			rduclutch = v[(0xd1, 0x1d)][0]*2 - 40

			debug('\r[{}] PTU Oil: {}C, RDU Oil: {}C, RDU Clutch: {}C, L/R Clutch: {}/{}C      '.format(t,
				int(ptuoil), rduoil, rduclutch, int(lclutch), int(rclutch)), end='')
			sleep(1)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		debug('\n[+] Done.')
		pass

	input()