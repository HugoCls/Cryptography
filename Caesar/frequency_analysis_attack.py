from caesar import caesar_to_text

def frequencyAnalyser(text):
    """
    Analyzes the frequency of alphabetic characters in the given text.

    Args:
    - text (str): The input text to analyze.

    Returns:
    - list: A sorted list of tuples containing the frequency of each alphabetic character.
            Each tuple has the format (character, frequency).
    """
    dict = {}
    # going through each character of the string
    for chr in text:
        # if the character is an alphabetic, we will count the appearances
        if ((chr >= 'a' and chr <= 'z') or (chr >= 'A' and chr <= 'Z')):
            chr = chr.lower()
            # total[c] += 1

            if dict.get(chr) is not None:
                dict[chr] += 1
            else:
                dict[chr] = 1
    #return dict
    return sorted(dict.items(), key=lambda x:x[1], reverse=True)


if __name__ == "__main__":

    # My key based on the keys you asked to choose with our names (7)
    key = (ord('H') - ord('A')) % 26

    # Read the message
    with open("message.txt", "r", encoding="utf-8") as file:
        text = file.read()

    # Encrypt the message and save it to a file
    ciphertext = caesar_to_text(text, key)

    with open("encrypted.txt", "w", encoding="utf-8") as file:
        text = file.write(ciphertext)

    # Launch a frequency analysis and get the most common letter
    frequency_analysis = frequencyAnalyser(ciphertext)
    most_common_letter = frequency_analysis[0][0]

    # Suppose that the most common letter corresponds to 'e' according to analysis on natural english speaking
    shift = (ord(most_common_letter) - ord('e')) % 26

    # Decypher the text
    decrypted_text = caesar_to_text(ciphertext, shift, action="decrypt")

    # Save the decyphered text into a file
    with open("decyphered_message.txt", "w", encoding="utf-8") as file:
        file.write(decrypted_text)