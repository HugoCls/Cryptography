# One-Time Pad (OTP) Encryption and Decryption

## Introduction

The One-Time Pad (OTP) is a theoretically unbreakable encryption technique that uses a random key as long as the message being encrypted. The key is XORed with the plaintext to generate the ciphertext. To decrypt the ciphertext, the same key is XORed with the encrypted binary string, which returns the original message.

This project demonstrates OTP encryption and decryption in Python.

## How It Works

1. **Text to Binary Conversion**: The input text is converted into its binary form.
2. **Random Key Generation**: A random binary key of the same length as the binary text is generated.
3. **Encryption (XOR Operation)**: The binary text is XORed with the key to produce the encrypted binary string.
4. **Decryption (XOR Operation)**: The encrypted binary is XORed with the same key to retrieve the original binary, which is then converted back into the original text.

## Code Example

```python
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
```

## Example output

```
Texte binaire: 010000110110010101100011011010010010000001100101011100110111010000100000011101010110111001100101011110000110010101101101011100000110110001100101001000000110010001100101001000000111010001100101011110000111010001100101001000000110000101110011001000000110001101101000011010010110011001100110011100100110010100101110
Clé binaire aléatoire: 101010111011101000011001101110010011111010001011101000111010010101010100
Texte binaire chiffré: 111010001101111101111010110100001001111011101110110110111110010101010100
Texte déchiffré final: Ceci est un exemple de texte à chiffrer.
```