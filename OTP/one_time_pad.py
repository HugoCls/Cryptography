import random

def otp(text):

    binary_str = ' '.join(format(ord(char), '08b') for char in text)
    binary_text = ''.join(binary_str.split())

    key = ''.join(str(random.randint(0,1)) for _ in range(len(binary_text)))

    # XOR the key with the text binary
    encrypted_binary = ''.join(str(int(bit1) ^ int(bit2)) for bit1, bit2 in zip(binary_text, key))

    decrypted_binary = ''.join(str(int(bit1) ^ int(bit2)) for bit1, bit2 in zip(encrypted_binary, key))
    decrypted_text = ''.join(chr(int(decrypted_binary[i:i+8], 2)) for i in range(0, len(decrypted_binary), 8))


    print("Texte binaire:", binary_text)
    print("Clé binaire aléatoire:", key)
    print("Texte binaire chiffré:", encrypted_binary)
    print("Texte déchiffré final:", decrypted_text)

text = "Ceci est un exemple de texte à chiffrer."

otp(text)

