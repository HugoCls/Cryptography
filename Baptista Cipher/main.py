from baptista import encrypt, decrypt
from image_processing import load_image, save_image

if __name__ == "__main__":
    ### PARAMETERS ###
    _x0 = 0.1
    r = 3.81
    xmin = 0.0
    xmax = 1.0
    p = 0.5

    ### BAPTISTA CIPHERING ON TEXT ###
    """
    with open('data/plaintext.txt', 'r') as f:
        plaintext = f.read().strip()

    # Convert text into ASCII numbers
    data = [ord(char) for char in plaintext]

    # Encryption
    ciphertext = encrypt(data, _x0, r, xmin, xmax, p)
    print("Ciphertext:", ciphertext)

    # Decryption
    decrypted_data = decrypt(ciphertext, len(ciphertext), _x0, r, xmin, xmax)
    print("Decrypted data:", decrypted_data)

    # Convert decrypted data into text
    decrypted_text = ''.join(chr(char) for char in decrypted_data)
    print("Decrypted text:", decrypted_text)

    ### Save the data ###
    with open('data/cipheredtext_data.txt', 'w') as f:
        f.write(f"{ciphertext}")
    
    with open('data/deciphered_text.txt', 'w') as f:
        f.write(f"{decrypted_text}")
    """
    #### BAPTISTA CIPHERING ON IMAGE ####

    # Load and prepare image data for encryption
    data, width, height, mode = load_image('data/image.jpg')
    print(f"Image_data: {data[:20]}")
    print(f"Image.mode: {mode}")
    # Encrypt the image data
    cipher_img_data = encrypt(data, _x0, r, xmin, xmax, p)
    print("Ciphered_image_data:", cipher_img_data[:20])

    # Decrypt the image data
    decrypted_data = decrypt(cipher_img_data, len(cipher_img_data), _x0, r, xmin, xmax)
    print("Decrypted_image_data:", decrypted_data[:20])

    ### Save the data ###
    with open('data/cipheredimage_data.txt', 'w') as f:
        f.write(f"{cipher_img_data}")

    for i in range(len(cipher_img_data)):
        cipher_img_data[i] = cipher_img_data[i] % 256

    # Save the decrypted image
    save_image(cipher_img_data, width, height, mode, 'data/encrypted_image.jpg')

    # Save the decrypted image
    save_image(decrypted_data, width, height, mode, 'data/decrypted_image.jpg')