import socket, struct, binascii
from hashlib import md5

from MijiaDevice import MijiaDevice
from MijiaPacket import MijiaPacket

from Discovery import Discovery


discoverer = Discovery()
devices = discoverer.discover()

for devId in devices:
	device = devices[devId]
	print("Device ID:", devId)
	print("Model:", device.model)
	print("Device class:", device.type)
	print("Hostname:", device.hostname)
	print("Address:", device.address)
	# print("Stamp: ", device.stamp
	print("Token:", binascii.hexlify(device.token))
	# print("TokenKey: ", binascii.hexlify(device.tokenKey()))
	# print("TokenIV: ", binascii.hexlify(device.tokenIV()))

	# packet = MijiaPacket()
	#print(device.getInfo())
	#print(device.call('get_status'))
	print("Properties:", device.getProperties())
	# if device.model == 'chuangmi.plug.m1':
	# 	print(device.getProperties(['power', 'mode', 'load_power', 'power_consumed']))

	# if device.model == 'zimi.powerstrip.v2':
	# 	print(device.getProperties(['power', 'mode', 'load', 'consumed']))

	if device.model == 'lumi.gateway.v3':
		device.call('set_rgb', [0])
		subdevices = device.getSubdevices()
		#device.initDeveloperAPI()
		for sid in subdevices.keys():
			sub = subdevices[sid]
			print("Subdevice:", sub.deviceId)
			print("Subdevice type:", sub.type)
			print("Properties:", sub.getProperties())

	print();