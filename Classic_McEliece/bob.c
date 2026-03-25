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
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    unsigned char pk[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_SECRETKEYBYTES];
    unsigned char ciphertext[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES];
    unsigned char decrypted_key[PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_BYTES];
    unsigned char encrypted_message[BUFFER_SIZE];
    unsigned char decrypted_message[BUFFER_SIZE];

    double key_creation_start_time = get_time_ms();
    {
        // Generate McEliece key pair
        if (PQCLEAN_MCELIECE6960119F_CLEAN_crypto_kem_keypair(pk, sk) != 0) {
            handle_errors("Key generation failed");
        }
    }
    double key_creation_time = get_time_ms() - key_creation_start_time;
    save_results("mceliece_key_creation_results.txt", key_creation_time);

    printf("Key generation successful.\n");
    if (!FAST_RUN)
        print_hex("Public Key", pk, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES);

    // Create socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        handle_errors("Socket failed");
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        handle_errors("setsockopt");
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Bind the socket to the network address and port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        handle_errors("Bind failed");
    }

    // Listen for incoming connections
    if (listen(server_fd, 3) < 0) {
        handle_errors("Listen failed");
    }

    // Accept an incoming connection
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0) {
        handle_errors("Accept failed");
    }

    // Send public key to client
    ssize_t sent_bytes = send_all(new_socket, pk, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES);
    if (sent_bytes != PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_PUBLICKEYBYTES) {
        handle_errors("Failed to send public key");
    }
    printf("Public key sent to client.\n");

    // Receive encrypted message from client
    ssize_t received_bytes = recv_all(new_socket, ciphertext, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES);
    if (received_bytes != PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES) {
        handle_errors("Failed to receive ciphertext");
    }
    printf("Ciphertext received from client.\n");
    if (!FAST_RUN)
        print_hex("Ciphertext", ciphertext, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_CIPHERTEXTBYTES);

    double decryption_start_time = get_time_ms();
    {
        // Decrypt the received message
        if (PQCLEAN_MCELIECE6960119F_CLEAN_crypto_kem_dec(decrypted_key, ciphertext, sk) != 0) {
            handle_errors("Decryption failed");
        }
    }
    double decryption_creation_time = get_time_ms() - decryption_start_time;
    save_results("mceliece_decryption_results.txt", decryption_creation_time);
    
    printf("Decryption successful.\n");
    if (!FAST_RUN)
        print_hex("Decrypted Shared Secret Key", decrypted_key, PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_BYTES);

    if (!FAST_RUN)
    {
        // Receive the length of the encrypted message from the client
        uint32_t message_len;
        received_bytes = recv_all(new_socket, &message_len, sizeof(message_len));
        if (received_bytes != sizeof(message_len)) {
            handle_errors("Failed to receive message length");
        }
        message_len = ntohl(message_len); // Convert to host byte order

        // Receive encrypted message from client
        received_bytes = recv_all(new_socket, encrypted_message, message_len);
        if (received_bytes != message_len) {
            handle_errors("Failed to receive encrypted message");
        }
        printf("Encrypted message received from client.\n");
        print_hex("Encrypted Message", encrypted_message, received_bytes);

        // Decrypt the message using the shared secret key (simple XOR)
        for (uint32_t i = 0; i < message_len; i++) {
            decrypted_message[i] = encrypted_message[i] ^ decrypted_key[i % PQCLEAN_MCELIECE6960119F_CLEAN_CRYPTO_BYTES];
        }
        decrypted_message[message_len] = '\0';
        printf("Decrypted Message: %s\n", decrypted_message);
    }

    close(new_socket);
    close(server_fd);

    return 0;
}
