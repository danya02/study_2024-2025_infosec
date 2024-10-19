print('Plaintext:')
plaintext = bytes.fromhex(input('> '))
try:
    plaintext_text = plaintext.decode('cp1251')
    print('Plaintext как CP1251:')
    print(plaintext_text)
except:
    print('Plaintext не CP1251')

print()
print('Key:')
key = bytes.fromhex(input('> '))

if len(plaintext) != len(key):
    print('Plaintext и key должны быть одной и той же длины')

print()
print('Ciphertext:')
ciphertext = bytes([a ^ b for a, b in zip(plaintext, key)])
print(ciphertext.hex(' '))
try:
    ciphertext_text = ciphertext.decode('cp1251')
    print('Ciphertext как CP1251:')
    print(ciphertext_text)
except:
    print('Ciphertext не CP1251')