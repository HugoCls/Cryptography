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

void save_results_alice(const char *filename, const char *plaintext, unsigned char *ciphertext, double key_creation_time, double encryption_time) {
    FILE *file = fopen(filename, "a");
    if (file != NULL) {
        // Remplace les sauts de ligne par des espaces
        char *plaintext_str = strdup(plaintext);
        char *ciphertext_str = strdup((char *)ciphertext);
        char *ptr;
        while ((ptr = strchr(plaintext_str, '\n')) != NULL) {
            *ptr = ' ';
        }
        while ((ptr = strchr(ciphertext_str, '\n')) != NULL) {
            *ptr = ' ';
        }

        // Écriture dans le fichier
        fprintf(file, "%s::%s::%.15g::%.15g\n", plaintext_str, ciphertext_str, key_creation_time, encryption_time);

        // Nettoyage
        free(plaintext_str);
        free(ciphertext_str);

        fclose(file);
    } else {
        printf("Erreur lors de l'ouverture du fichier %s\n", filename);
    }
}

#define BOB_PORT 8080

void handleErrors() {
    ERR_print_errors_fp(stderr);
    abort();
}

RSA *generate_rsa_keypair() {
    RSA *rsa = RSA_new();
    BIGNUM *e = BN_new();
    BN_set_word(e, RSA_F4);
    if (!RSA_generate_key_ex(rsa, 2048, e, NULL)) {
        handleErrors();
    }
    BN_free(e);
    return rsa;
}

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    RSA *rsa = NULL;
    
    // Generate RSA key pair
    double key_creation_start_time = get_time_ms();
    rsa = generate_rsa_keypair();
    double key_creation_time = get_time_ms() - key_creation_start_time;

    // Print Alice's public key
    char *pub_key_hex;
    {
        BIO *bp_public = BIO_new(BIO_s_mem());
        PEM_write_bio_RSAPublicKey(bp_public, rsa);
        BUF_MEM *bptr;
        BIO_get_mem_ptr(bp_public, &bptr);
        pub_key_hex = (char *)malloc(bptr->length + 1);
        memcpy(pub_key_hex, bptr->data, bptr->length);
        pub_key_hex[bptr->length] = '\0';
        BIO_free(bp_public);
        printf("Alice's Public Key: %s\n", pub_key_hex);
    }

    // Initialize connection to Bob
    {
        // Create socket
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            printf("\nSocket creation error \n");
            return -1;
        }
        
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(BOB_PORT);
        // Convert string to IP address (localhost)
        if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
            printf("\nInvalid address / Address not supported \n");
            return -1;
        }

        // Connect to server
        if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
            printf("\nConnection Failed \n");
            return -1;
        }
    }
    
    // Send Alice's public key to Bob
    send(sock, pub_key_hex, strlen(pub_key_hex) + 1, 0);

    // Message to encrypt
    unsigned char plaintext[] = "Hello, world!";

    // Length of the plaintext
    int plaintext_len = strlen((char *)plaintext);
    
    // Buffer for the ciphertext
    unsigned char *ciphertext = malloc(RSA_size(rsa));

    printf("Plaintext: %s\n", plaintext);

    // Encryption
    double encryption_start_time = get_time_ms();
    if (RSA_public_encrypt(plaintext_len, plaintext, ciphertext, rsa, RSA_PKCS1_PADDING) == -1) {
        handleErrors();
    }
    double encryption_time = get_time_ms() - encryption_start_time;

    printf("Ciphertext: ");
    for (int i = 0; i < RSA_size(rsa); ++i) {
        printf("%02x", ciphertext[i]);
    }
    printf("\n");

    // Send the ciphertext to Bob
    send(sock, ciphertext, RSA_size(rsa), 0);

    // Free allocated memory
    free(ciphertext);
    RSA_free(rsa);
    close(sock);
    
    // Save encryption results
    save_results_alice("alice_results.txt", plaintext, ciphertext, key_creation_time, encryption_time);

    return 0;
}
