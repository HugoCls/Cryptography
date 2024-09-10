# Caesar Cipher Encryption and Decryption

The Caesar Cipher is one of the simplest and most widely known encryption techniques. It is a type of substitution cipher where each letter in the plaintext is shifted by a fixed number of positions down or up the alphabet. The number of positions to shift is known as the "key."

For example, with a key of 3, 'A' becomes 'D', 'B' becomes 'E', and so on. After reaching the end of the alphabet, the cipher wraps around (e.g., 'Z' becomes 'C').

### Example

- Plaintext: `HELLO`
- Key: `3`
- Ciphertext: `KHOOR`

## Cryptanalysis: Frequency Analysis

One major weakness of the Caesar Cipher is that it is vulnerable to **frequency analysis**. Since it is a substitution cipher, each letter in the ciphertext corresponds to a letter in the plaintext. In any given language, certain letters appear more frequently than others.

### Steps of Frequency Analysis:
1. **Letter Frequency**: By analyzing the frequency of each letter in the ciphertext, it is possible to identify patterns. For example, in English, 'E' is the most common letter, followed by 'T', 'A', 'O', etc.
2. **Pattern Matching**: Compare the frequency of letters in the ciphertext to the known frequency distribution of letters in the target language (e.g., English).
3. **Guessing the Key**: By aligning the most frequent letters in the ciphertext with the most frequent letters in the language, you can make an educated guess about the key used for encryption.
4. **Brute Force**: Since there are only 25 possible shifts (keys) in the Caesar Cipher, a brute-force approach is feasible, where each shift is tried until the plaintext is revealed.

### Example of Frequency Distribution (in English):

| Letter | Frequency (%) |
|--------|---------------|
| E      | 12.70         |
| T      | 9.06          |
| A      | 8.17          |
| O      | 7.51          |
| I      | 6.97          |
| N      | 6.75          |
| S      | 6.33          |
| H      | 6.09          |

By using this distribution, you can analyze the ciphertext and try to match the most frequent letters to crack the Caesar Cipher.

## Conclusion

While the Caesar Cipher is simple and easy to implement, it is not secure by modern standards. It can be easily broken through brute force or frequency analysis, especially for messages in common languages like English, where the frequency distribution of letters is well known.

