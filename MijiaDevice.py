import re, struct, time
from hashlib import md5
from socket import gethostbyaddr

from MijiaPacket import MijiaPacket
from MijiaSubdevice import MijiaSubdevice

DeviceClasses = {
	'zhimi.airpurifier.v1': "AirPurifier",
	'zhimi.airpurifier.v2': "AirPurifier",
	'zhimi.airpurifier.v3': "AirPurifier",
	'zhimi.airpurifier.m1': "AirPurifier",
	'zhimi.airpurifier.v6': "AirPurifier",

	'zhimi.humidifier.v1': "Humidifier",

	'chuangmi.plug.m1': "PowerPlug",
	'chuangmi.plug.v1': "chuangmi.plug.v1",
	'chuangmi.plug.v2': "PowerPlug",

	'rockrobo.vacuum.v1': "Vacuum",

	'lumi.gateway.v2': "Gateway",
	'lumi.gateway.v3': "Gateway",
	'lumi.acpartner.v1': "Gateway",

	'qmi.powerstrip.v1': "PowerStrip",
	'zimi.powerstrip.v2': "PowerStrip",

	'yeelink.light.lamp1': "yeelight.lamp",
	'yeelink.light.mono1': "yeelight.mono",
	'yeelink.light.color1': "yeelight.color"
}

DeviceProperties = {
	'PowerPlug': [
		{
			'name': 'power',
			'parse': lambda x : x
		}
	],
	'PowerStrip': [
		{
			'name': 'power',
			'parse': lambda x : x
		}
	],
	'Gateway': [
		{
			'name': 'illumination',
			'parse': lambda x : x
		},
		{
			'name': 'rgb',
			'parse': lambda x : x
		}
	]
}


class MijiaDevice():
	def __init__(self, buf, addr):
		self.buf = buf
		self.address = addr
		self.deviceId = self.getDeviceId()
		self.stamp = self.getStamp()
		self.stampTime = int(time.time())
		self._packetId = 0
		self.token = self.getToken()
		self.tokenKey = self.getTokenKey()
		self.tokenIV = self.getTokenIV()
		self.hostname = self.getHostname()
		(self.model, self.type) = self.getModel()
		self.properties = DeviceProperties[self.type]

		# Packet for communicating with this device
		self.packet = MijiaPacket()


	def extractInt(self, offset):
		return struct.unpack(">L", self.buf[offset:offset+4])[0]

	def getDeviceId(self):
		return self.extractInt(8)

	def getStamp(self):
		return self.extractInt(12)

	def getToken(self):
		return self.buf[16:]

	def getTokenKey(self):
		hash = md5()
		hash.update(self.token)
		return hash.digest()

	def getTokenIV(self):
		hash = md5()
		hash.update(self.tokenKey)
		hash.update(self.token)
		return hash.digest()

	def getHostname(self):
		host = gethostbyaddr(self.address)
		return host[0]

	def getModel(self):
		r = re.compile('(.+)_miio(\d+)')
		m = r.search(self.hostname)
		if m is None:
			# Fallback for rockrobo - might break in the future
			if self.hostname.find('rockrobo') > -1:
				return ('rockrobo.vacuum.v1', 'vacuum')

			return (None, None)

		model = m.group(1).replace('-', '.')
		if model in DeviceClasses:
			return (model, DeviceClasses[model])

		return (model, 'generic')

	def getNextPacketId(self):
		if self._packetId == 10000:
			self._packetId = 0

		self._packetId += 1
		return self._packetId

	def call(self, method, args=[]):
		return self.packet.call(self, method, args)

	def getInfo(self):
		return self.call('miIO.info')

	def getProperties(self):
		props = [prop['name'] for prop in self.properties]
		data = self.call('get_prop', props)['result']
		print('<-', data)
		results = []
		for i in range(0, len(data)):
			prop = self.properties[i]
			if prop['name'] == 'rgb':
				rgba = data[i]

				result = {
					'name': 'rgb'
				}
				result['value'] = {
					'red': 0xff & (rgba >> 16),
					'green': 0xff & (rgba >> 8),
					'blue': 0xff & rgba
				}
				results.append(result)

				result = {
					'name': 'brightness',
					'value': int(0xff & (rgba >> 24))
				}
				results.append(result)
			else:
				result = {
					'name': prop['name'],
					'value': prop['parse'](data[i])
				}
				results.append(result)
		return results

	def getDeviceProperties(self, props):
		return self.call('get_device_prop', props)

	def getDevApiKey(self):
		key = self.call('get_lumi_dpf_aes_key')
		if 'result' in key and len(key['result'][0]) == 16:
			apiKey = key['result'][0]
		else:
			apiKey = 'generate-key-here'

		return apiKey

	def getSubdevices(self):
		response = self.getDeviceProperties(['lumi.0', 'device_list'])
		subs = response['result']
		subs = [subs[i:i + 5] for i in range(0, len(subs), 5)]

		subdevices = {}
		for sub in subs:
			subdevices[sub[0]] = MijiaSubdevice(self, sub)

		return subdevices