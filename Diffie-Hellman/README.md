# Diffie-Hellman Key Exchange

The **Diffie-Hellman** key exchange is a method that allows two parties to securely share a cryptographic key over a public channel. It was one of the first public-key protocols and remains fundamental to secure communication today.

## How It Works

1. **Public Parameters**: Both parties agree on two public values: a large prime number `p` and a base `g`.
2. **Private Keys**: Each party selects a private key, a secret random number (`a` for Alice, `b` for Bob).
3. **Exchange**: 
   - Alice computes `A = g^a mod p` and sends it to Bob.
   - Bob computes `B = g^b mod p` and sends it to Alice.
4. **Shared Secret**: 
   - Alice computes `s = B^a mod p`.
   - Bob computes `s = A^b mod p`.
   
Both arrive at the same shared secret `s`, which can be used as a cryptographic key for secure communication.

## Security

The security of Diffie-Hellman is based on the **discrete logarithm problem**, which is computationally difficult to reverse. Even though `g`, `p`, `A`, and `B` are publicly known, an attacker cannot easily compute the shared secret without knowing the private keys.

## Vulnerabilities

Diffie-Hellman is vulnerable to **man-in-the-middle attacks** if the initial key exchange isn't authenticated, as an attacker can intercept and replace public values. However, this can be mitigated by using authenticated key exchange protocols like **Digital Signatures**.