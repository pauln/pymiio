from hashlib import md5
from Crypto.Cipher import AES


# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                bytes(chr(BLOCK_SIZE - len(s) % BLOCK_SIZE), 'utf-8')
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class AESCipher:
    """
    Usage:
        c = AESCipher('password').encrypt('message')
        m = AESCipher('password').decrypt(c)

    Tested under Python 3 and PyCrypto 2.6.1.

    """

    def __init__(self, key):
        self.key = key#md5(key).digest()

    def encrypt(self, raw, iv):
        raw = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(raw)

    def decrypt(self, enc, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))

