import index_of_coincidence
from frequency_analysis import Chi_square_approach
from vigenere import vigenere_to_text


## ENCRYPTION PART ##
with open("message.txt", "r", encoding="utf-8") as f:
    plaintext = f.read()

key = "HUGO"

# Encipher the text
ciphertext = vigenere_to_text(plaintext=plaintext, key=key, action="encrypt")

with open('encrypted.txt', 'w', encoding="utf-8") as f:
    f.write(ciphertext)

## DECRYPTION PART ##

## FIND THE KEY LENGHT

# Index of Coincidence approach (based on letters percentage of apparition on english Language, ICenglish)
key_length = index_of_coincidence.find_key_length(ciphertext=ciphertext, max_key_len=10)
print(f"Guessed key_lenght(index of coincidence): {key_length}")


## FIND THE KEY

# Chi-square approach
decryptedtext, guessedkey = Chi_square_approach(ciphertext, key_length)
print(f"Guessed key(Chi-square): {guessedkey}")

## SAVE THE RESULT
with open("decrypted.txt", "w", encoding="utf-8") as f:
    f.write(vigenere_to_text(ciphertext, key=guessedkey, action="decrypt"))