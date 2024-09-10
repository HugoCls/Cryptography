

def caesar_to_text(plaintext, key, action="encrypt"):
    '''
    Returns the encrypted or the decrypted version of a plaintext using the ceasar algorithm and [key] as a key of encryption.

    Parameters:
            plaintext (str): The text to encrypt
            key (int): The actual key
            action ["encrypt",] (str): wether the text has to be encrypted or decrypted

    Returns:
            cryptogram (str): The encrypted version of our text
    '''

    cryptogram = ""

    # iterate over the given text
    for k in range(len(plaintext)):

        ch = plaintext[k]

        # We encrypt or decrypt the caracter depending of the user's choice
        if action == "encrypt":
            cryptogram += caesar_to_chr(ch, key)

        else:
            cryptogram += caesar_to_chr(ch, -key)

    return cryptogram
    

def caesar_to_chr(ch, key):
    '''
    Encrypt/Decrypt a caracter using caesar algorithm and [key] as a key.
    
    For any special caracter, it does just return the same caracter

    Parameters:
            ch (str): The actual caracter to be encrypted/decrypted
            key (int): The actual key
    
    Returns:
            new_ch (str): The encrypted version of our text
    '''

    if ch in [" ", "\n"] or ord(ch) not in [lower_k for lower_k in range(65, 65+26)] + [upper_k for upper_k in range(97, 97+26)]:
        new_ch = ch
        # check if a character is uppercase then encrypt it accordingly
    
    elif (ch.isupper()):
        new_ch = chr((ord(ch) + key - 65) % 26 + 65)
        # check if a character is lowercase then encrypt it accordingly
    
    else:
        new_ch = chr((ord(ch) + key - 97) % 26 + 97)

    return new_ch