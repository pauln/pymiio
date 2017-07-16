import socket

from MijiaDevice import MijiaDevice


PORT = 54321
PING_DATA = "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
SEARCH_ITERATIONS = 2

class Discovery():
	def _discover(self):
		# SOCK_DGRAM is the socket type to use for UDP sockets
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.settimeout(2)

		# As you can see, there is no connect() call; UDP has no connections.
		# Instead, data is directly sent to the recipient via sendto().
		data = bytes.fromhex(PING_DATA)
		sock.sendto(data, ('<broadcast>', PORT))
		devices = []
		(msg, addr) = sock.recvfrom(1024)
		while (msg is not None):
			devices.append(MijiaDevice(msg, addr[0]))

			try:
				(msg, addr) = sock.recvfrom(1024)
			except:
				break

		return devices

	def discover(self):
		devices = {}
		for i in range(1, SEARCH_ITERATIONS):
			for device in self._discover():
				devId = device.deviceId
				if devId not in devices:
					devices[devId] = device

		return devices