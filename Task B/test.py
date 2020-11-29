import hashlib
import os
password = b'admin1'
key = b''
salt = os.urandom(8)
print(salt.hex())
print(bytes.fromhex(salt.hex())== salt)

dk = hashlib.pbkdf2_hmac('sha256', password,bytes.fromhex("77aa3edd22766057") , 100000)
print(dk.hex())

new_key = hashlib.pbkdf2_hmac(
    'sha256',
    b"admin1", # Convert the password to bytes
    salt, 
    100000
)
if new_key == dk:
    print('Password is correct')
else:
    print('Password is incorrect')

