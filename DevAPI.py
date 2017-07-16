import json, re, socket, struct, sys, time

from MijiaPacket import MijiaPacket
from MijiaDevice import MijiaDevice
from MijiaSubdevice import MijiaSubdevice

MULTICAST_ADDRESS = '224.0.0.50'
MULTICAST_PORT = 4321
MULTICAST_BIND_PORT = 9898

class DevAPI():
	def __init__(self, gateway, apiKey):
		self.gateway = gateway
		self.apiKey = apiKey
		self.connected = False
		self.socket = None
		self.lastHeartbeat = time.time()
		self.subdevices = gateway.getSubdevices()

	def ipIsLocal(self, ip):
		regex = "(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)"
		return re.match(regex, ip) is not None

	def getLocalIp(self):
		# Extract just the IP addresses
		info = socket.getaddrinfo(socket.gethostname(), 80)
		ips = [x[4][0] for x in info if self.ipIsLocal(x[4][0])]

		local = ips[0] if len(ips) > 0 else None

		# Fallback
		if not local:
			temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			try:
				temp.connect((self.gateway.address, 9))
				local = temp.getsockname()[0]
			except socket.error:
				# If all else fails, just return regular localhost ip
				local = "127.0.0.1"
			finally:
				temp.close()

		return local

	def connect(self):
		local = self.getLocalIp()
		print("Local IP:", local)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local))
		self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

		request = socket.inet_aton(MULTICAST_ADDRESS) + socket.inet_aton(local)
		self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, request)

		bindTo = local
		if sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
			bindTo = '0.0.0.0'
		
		self.socket.bind((bindTo, MULTICAST_BIND_PORT))

		self.connected = True

		print("Connected to Dev API")

	def disconnect(self):
		self.socket.close()
		self.connected = False

	def listen(self):
		if not self.connected:
			self.connect()

		while self.connected:
			data, address = self.socket.recvfrom(1024)
			self.processPacket(data, address)

			secondsSinceHeartbeat = int(time.time() - self.lastHeartbeat)
			if secondsSinceHeartbeat > 120:
				# No heartbeat seen for > 2 minutes.  Disconnect and try again.
				self.disconnect()
				self.connect()

	def processPacket(self, data, address):
		if address[0] == self.gateway.address:
			# Gateway seems to skip heartbeats if actual data packets were sent
			# so we consider any valid packet from the gateway to be a heartbeat.
			self.lastHeartbeat = time.time()

			# Multicast packets are simply raw json - parse!
			packet = json.loads(data.decode('utf-8'))

			if packet['model'] == 'gateway' and packet['cmd'] == 'heartbeat':
				# We don't care about this packet - we've already updated our heartbeat time.
				return
			elif packet['cmd'] == 'report':
				if packet['model'] == 'gateway':
					model = self.gateway.model
				else:
					sid = 'lumi.'+packet['sid']
					if sid not in self.subdevices:
						self.subdevices = self.gateway.getSubdevices()

					if sid in self.subdevices:
						subtype = self.subdevices[sid].type
					else:
						subtype = "unknown"
				
				print('lumi.'+packet['sid'], '('+subtype+')', '-', packet['data'])
		else:
			print("Unexpected packet from", address, "-", data)
