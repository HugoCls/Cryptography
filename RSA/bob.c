#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <time.h>

double get_time_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

void save_results_bob(const char *filename, unsigned char *decrypted_text, unsigned char *ciphertext, double decryption_time) {
    FILE *file = fopen(filename, "a");
    if (file != NULL) {
        // Remplace les sauts de ligne par des espaces
        char *ciphertext_str = strdup((char *)ciphertext);
        char *decrypted_text_str = strdup((char *)decrypted_text);
        char *ptr;
        while ((ptr = strchr(ciphertext_str, '\n')) != NULL) {
            *ptr = ' ';
        }
        while ((ptr = strchr(decrypted_text_str, '\n')) != NULL) {
            *ptr = ' ';
        }

        // Écriture dans le fichier
        fprintf(file, "%s::%s::%.15g\n", ciphertext_str, decrypted_text_str, decryption_time);

        // Nettoyage
        free(ciphertext_str);
        free(decrypted_text_str);

        fclose(file);
    } else {
        printf("Erreur lors de l'ouverture du fichier %s\n", filename);
    }
}

#define SERVER_PORT 8080

void handleErrors(void) {
    ERR_print_errors_fp(stderr);
    abort();
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    RSA *rsa = NULL;

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(SERVER_PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 10) < 0) {
        perror("Listen");
        exit(EXIT_FAILURE);
    }

    printf("Bob is waiting for connections...\n");

    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
        perror("Accept");
        exit(EXIT_FAILURE);
    }

    // Receive Alice's public key
    char alice_pub_key_hex[2048];
    int bytes_read = read(new_socket, alice_pub_key_hex, 2048);
    if (bytes_read < 0) {
        handleErrors();
    }
    
    printf("Bob received Alice's public key: %s\n", alice_pub_key_hex);

    // Loading Alice's public key
    rsa = PEM_read_bio_RSAPublicKey(BIO_new_mem_buf(alice_pub_key_hex, strlen(alice_pub_key_hex)), NULL, NULL, NULL);
    if (!rsa) {
        handleErrors();
    }

    // Receive ciphertext from Alice
    unsigned char ciphertext[2048] = {0};
    int ciphertext_len = read(new_socket, ciphertext, 2048);
    if (ciphertext_len < 0) {
        handleErrors();
    }

    printf("Received ciphertext: ");
    for (int i = 0; i < ciphertext_len; ++i) {
        printf("%02x", ciphertext[i]);
    }
    printf("\n");

    // Decryption
    double decryption_start_time = get_time_ms();
    unsigned char *decrypted_text = malloc(RSA_size(rsa));
    int decrypted_text_len = RSA_public_decrypt(ciphertext_len, ciphertext, decrypted_text, rsa, RSA_PKCS1_PADDING);
    if (decrypted_text_len == -1) {
        handleErrors();
    }
    double decryption_time = get_time_ms() - decryption_start_time;

    decrypted_text[decrypted_text_len] = '\0'; // Null-terminate the decrypted text
    printf("Decrypted text: %s\n", decrypted_text);

    // Save results
    save_results_bob("bob_results.txt", decrypted_text, ciphertext, decryption_time);

    // Cleanup
    free(decrypted_text);
    RSA_free(rsa);
    close(new_socket);

    return 0;
}
