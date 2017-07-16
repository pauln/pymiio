GatewaySubdevices = {
	# Switch (button) controller
	1: {
		'type': 'switch',
		'properties': []
	},
	# Motion sensor
	2: {
		'type': 'motion',
		'properties': []
	}	,
	# Magnet sensor for doors and windows
	3: {
		'type': 'magnet',
		'properties': [
			{
				'name': 'open',
				'parse': lambda x: x
			}
		]
	},

	# TODO: What is 4, 5 and 6? plug, 86sw1 and 86sw2 are left

	# Light switch with two channels
	7: {
		'type': 'ctrl_neutral2',
		'properties': []
	}	,
	# Cube controller
	8: {
		'type': 'cube',
		'properties': []
	}	,
	# Light switch with one channel
	9: {
		'type': 'ctrl_neutral1',
		'properties': []
	}	,
	# Temperature and Humidity sensor
	10: {
		'type': 'sensor_ht',
		'properties': [
			{
				'name': 'temperature',
				'parse': lambda x : x/100
			},
			{
				'name': 'humidity',
				'parse': lambda x : x/100
			}
		]
	},

	11: {
		'type': 'plug',
		'properties': []
	}	,

	# Light switch (live+neutral wire version) with one channel
	20: {
		'type': 'ctrl_ln1',
		'properties': []
	}	,
	# Light switch (live+neutral wire version) with two channels
	21: {
		'type': 'ctrl_ln2',
		'properties': []
	}	
}



class MijiaSubdevice():
	def __init__(self, gateway, meta):
		sub = GatewaySubdevices[meta[1]]
		self.gateway = gateway
		self.type = sub['type']
		self.deviceId = meta[0]
		self.properties = sub['properties']

	def call(self, method, args=[]):
		return self.gateway.call(method, args)

	def getProperties(self):
		props = [prop['name'] for prop in self.properties]
		if len(props) == 0:
			return []
			
		props.insert(0, self.deviceId)
		data = self.call('get_device_prop_exp', [props])['result'][0]
		print('<-', data)
		results = []
		for i in range(0, len(data)):
			prop = self.properties[i]
			result = {
				'name': prop['name'],
				'value': prop['parse'](data[i])
			}
			results.append(result)
		return results