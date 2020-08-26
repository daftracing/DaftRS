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

from subprocess import Popen, PIPE, TimeoutExpired
import os
import signal
import sys

dbgon = False

def die(str):
	print(str)
	sys.exit(-1)

def debug(str, end='\n', level='print'):
	global dbgon

	if level == 'print':
		print(str, end=end)
		sys.stdout.flush()

	if level == 'debug' and dbgon:
		print("[DBG] {}".format(str))

def run(cmd, shell=False, timeout=None, stdout=PIPE):	
	with Popen(cmd, shell=shell, stdout=stdout, preexec_fn=os.setsid) as process:
	    try:
	        output = process.communicate(timeout=timeout)[0]
	    except TimeoutExpired:
	        os.killpg(process.pid, signal.SIGINT)
	        output = process.communicate()[0]

	debug(output, level='debug')
	if output:
		return output.decode("utf-8")
	return None
