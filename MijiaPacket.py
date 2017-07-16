import binascii, json, socket, struct, time
from hashlib import md5
from AesCbc import AESCipher

PORT = 54321

class MijiaPacket:
	def __init__(self):
		self.header = bytearray(32)
		self.header[0] = 0x21
		self.header[1] = 0x31

		for i in range(4,32):
			self.header[i] = 0xff

	def call(self, device, method, args=[]):
		for i in range(4, 8):
			self.header[i] = 0x00

		struct.pack_into('>L', self.header, 8, device.deviceId)
		
		id = device.getNextPacketId()
		request = {
			'id': id,
			'method': method,
			'params': args
		}
		request_json = json.dumps(request)
		print('->', request_json)
		packed = bytes(request_json, 'utf-8')

		secondsPassed = int(time.time() - device.stampTime)
		struct.pack_into('>L', self.header, 12, device.stamp + secondsPassed)

		encrypted = AESCipher(device.tokenKey).encrypt(packed, device.tokenIV)

		struct.pack_into('>H', self.header, 2, len(encrypted)+32)

		checksum = md5()
		checksum.update(self.header[0:16])
		checksum.update(device.token)
		checksum.update(encrypted)
		self.header[16:] = checksum.digest()

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.settimeout(2)

		data = bytes(self.header + encrypted)

		sock.sendto(data, (device.address, PORT))

		msg = sock.recv(1024)

		return self.handleResponse(device, msg)

	def handleResponse(self, device, msg):
		encrypted = msg[16:]
		decrypted = AESCipher(device.tokenKey).decrypt(encrypted, device.tokenIV)
		decrypted = decrypted.decode('utf-8')

		return json.loads(decrypted)
