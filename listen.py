import socket, struct, binascii
from hashlib import md5

from MijiaDevice import MijiaDevice
from MijiaPacket import MijiaPacket
from Discovery import Discovery
from DevAPI import DevAPI


PORT = 54321
PING_DATA = "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
SEARCH_ITERATIONS = 2

discoverer = Discovery()
devices = discoverer.discover()

for devId in devices:
	device = devices[devId]

	if device.model == 'lumi.gateway.v3':
		print("Device ID:", devId)
		print("Model:", device.model)
		print("Device class:", device.type)
		print("Hostname:", device.hostname)
		print("Address:", device.address)

		key = device.getDevApiKey()
		api = DevAPI(device, key)
		api.listen()

	print();