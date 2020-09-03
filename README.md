# DaftRS
A set of tools to tweak and tune Focus RS in a user friendly manner.

This is a "front end" part of the effort to create an Open Source tuning stack for Ford Focus RS.

## Hardware
SocketCAN (https://en.wikipedia.org/wiki/SocketCAN) compatible interface is needed.

#### Carloop *Basic*
https://store.carloop.io/products/carloop-basic

or

https://store.carloop.io/products/carloop + https://store.particle.io/collections/wifi/products/photon

This is the preferred interface as custom Photon firmware (https://github.com/daftracing/Softstick)
with additional features is part of the project.

## Install
Clone this and other needed repos with:
```
git clone --recursive https://github.com/daftracing/DaftRS
```

Change interface queue discipline to pfifo_fast:
```
sudo sh -c 'echo "net.core.default_qdisc = pfifo_fast" >> /etc/sysctl.conf'
sudo sysctl --system
```

## Usage
#### RDU tuning
Generate custom VBFs (only once):
```
cd ./vbf
./build.sh
cd ..
```
then:
```
./flash_rdu.py
```

#### ABS/DriftStick
```
./flash_abs.py
```

#### rset.py tweaks
If using Carloop, run the script to setup inferace:
```
./devsetup.py
```
then:
```
./rset.py -h
usage: rset.py [-h] [--can CAN] mode [options [options ...]]

Set Focus RS specific options

positional arguments:
  mode        PCM [HSCAN], RDU [HSCAN], PDC [HSCAN], FENG [MSCAN], PATS [HSCAN]
  options     Mode specific options like help or get/set etc

optional arguments:
  -h, --help  show this help message and exit
  --can CAN   Can device to be used, can0 by default

If using MSCAN make sure to connect your CAN interface to Ford specific MSCAN OBD pins (3, 11) and to set the correct can bus speed (125k)!!!
```

