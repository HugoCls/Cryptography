#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#include "api.h"

#define PORT 8080
#define BUFFER_SIZE 1024
#define FAST_RUN 1

double get_time_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

void save_results(const char *filename, double key_creation_time) {
    FILE *file = fopen(filename, "a");
    if (file != NULL) {
     
        // Write in the file
        fprintf(file, "%.15g\n", key_creation_time);

        fclose(file);
    } else {
        printf("Erreur lors de l'ouverture du fichier %s\n", filename);
    }
}

void handle_errors(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

void print_hex(const char *label, const unsigned char *data, size_t length) {
    printf("%s: ", label);
    for (size_t i = 0; i < length; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

ssize_t send_all(int sock, const void *buf, size_t len) {
    size_t total = 0;
    const char *p = buf;
    while (total < len) {
        ssize_t n = send(sock, p + total, len - total, 0);
        if (n == -1) {
            return -1;
        }
        total += n;
    }
    return total;
}

ssize_t recv_all(int sock, void *buf, size_t len) {
    size_t total = 0;
    char *p = buf;
    while (total < len) {
        ssize_t n = recv(sock, p + total, len - total, 0);
        if (n == -1) {
            return -1;
        }
        total += n;
    }
    return total;
}

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    unsigned char pk[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES];
    unsigned char ciphertext[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES];
    unsigned char key[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_BYTES];
    unsigned char message[BUFFER_SIZE];
    unsigned char encrypted_message[BUFFER_SIZE];

    // Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        handle_errors("Socket creation error");
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        handle_errors("Invalid address/Address not supported");
    }

    // Connect to server
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        handle_errors("Connection Failed");
    }

    // Receive public key from server
    ssize_t received_bytes = recv_all(sock, pk, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES);
    if (received_bytes != PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES) {
        handle_errors("Failed to receive public key");
    }
    printf("Public key received from server.\n");
    if (!FAST_RUN)
        print_hex("Public Key", pk, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES);

    double encryption_start_time = get_time_ms();
    {
        // Generate the ciphertext using the received public key
        if (PQCLEAN_MCELIECE6960119F_CLEAN_crypto_kem_enc(ciphertext, key, pk) != 0) {
            handle_errors("Encryption failed");
        }
    }
    double encryption_creation_time = get_time_ms() - encryption_start_time;
    save_results("mceliece_encryption_creation_results.txt", encryption_creation_time);
    
    printf("Encryption successful.\n");
    if (!FAST_RUN)
    {
        print_hex("Ciphertext", ciphertext, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES);
        print_hex("Shared Secret Key", key, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_BYTES);
    }

    // Send the ciphertext to the server
    ssize_t sent_bytes = send_all(sock, ciphertext, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES);
    if (sent_bytes != PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES) {
        handle_errors("Failed to send ciphertext");
    }
    printf("Ciphertext sent to server.\n");

    if (!FAST_RUN)
    {
        // Get a message from the user
        printf("Enter a message to encrypt: ");
        fgets((char *)message, sizeof(message), stdin);
        message[strcspn((char *)message, "\n")] = '\0'; // Remove the newline character

        // Encrypt the message using the shared secret key (simple XOR)
        size_t message_len = strlen((char *)message);
        for (size_t i = 0; i < message_len; i++) {
            encrypted_message[i] = message[i] ^ key[i % PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_BYTES];
        }

        // Send the length of the encrypted message to the server
        uint32_t net_message_len = htonl(message_len); // Convert to network byte order
        sent_bytes = send_all(sock, &net_message_len, sizeof(net_message_len));
        if (sent_bytes != sizeof(net_message_len)) {
            handle_errors("Failed to send message length");
        }

        // Send the encrypted message to the server
        sent_bytes = send_all(sock, encrypted_message, message_len);
        if (sent_bytes != message_len) {
            handle_errors("Failed to send encrypted message");
        }
        printf("Encrypted message sent to server.\n");
        print_hex("Encrypted Message", encrypted_message, message_len);
    }

    close(sock);

    return 0;
}
