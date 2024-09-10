#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <openssl/dh.h>
#include <openssl/err.h>
#include <openssl/pem.h>
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


#define EVE_PORT 9090
#define BOB_PORT 8080

// Select connection to Bob or Eve
#define SERVER_PORT BOB_PORT

void handleErrors() {
    ERR_print_errors_fp(stderr);
    abort();
}

void xor_encrypt_decrypt(unsigned char *input, unsigned char *key, unsigned char *output, int input_len, int key_len) {
    for (int i = 0; i < input_len; ++i) {
        output[i] = input[i] ^ key[i % key_len];
    }
}

DH *load_dh_params(const char *file_name) {
    DH *dh = NULL;

    FILE *param_file = fopen(file_name, "r");

    // Exit if error
    if (!param_file) {
        perror("Unable to open DH parameter file");
        exit(EXIT_FAILURE);
    }

    // Read DH params
    dh = PEM_read_DHparams(param_file, NULL, NULL, NULL);

    // Close files
    fclose(param_file);

    // Exit if error
    if (!dh) {
        fprintf(stderr, "Error reading DH parameters from file\n");
        exit(EXIT_FAILURE);
    }

    // Generate DH key
    uint genResponse = DH_generate_key(dh);
    if (genResponse != 1) {
        handleErrors();
    }

    return dh;
}

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    const BIGNUM *pub_key = NULL, *priv_key = NULL;
    
    double key_creation_start_time = get_time_ms();

    DH *dh = load_dh_params("dhparams.pem");

    // Generate private and public keys
    DH_get0_key(dh, &pub_key, &priv_key);

    // Convert public key to HEX code
    char *pub_key_hex = BN_bn2hex(pub_key);

    // Print public key
    printf("Alice's Public Key: %s\n", pub_key_hex);

    // Initialize connection
    {
        // Create socket
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            printf("\nSocket creation error \n");
            return -1;
        }
        
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(SERVER_PORT);
        // Convert string to IP address (local host)
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
    
    // Send public key to the server
    send(sock, pub_key_hex, strlen(pub_key_hex) + 1, 0);
    // Read Bob's public key from the server
    char bob_pub_key_hex[2048] = {0};
    read(sock, bob_pub_key_hex, 2048);

    // Print Bob's public key
    printf("Received Bob's Public Key: %s\n", bob_pub_key_hex);

    // Convert received key from HEX to binary
    BIGNUM *bob_pub_key = NULL;
    BN_hex2bn(&bob_pub_key, bob_pub_key_hex);

    // Compute secret shared key
    unsigned char *secret = malloc(DH_size(dh));
    int secret_size = DH_compute_key(secret, bob_pub_key, dh);
    if (secret_size < 0) {
        handleErrors();
    }
    
    double key_creation_time = get_time_ms() - key_creation_start_time;

    // Cleanup DH resources
    OPENSSL_free(pub_key_hex);
    BN_free(bob_pub_key);
    DH_free(dh);
    close(sock);
    
    double encryption_start_time = get_time_ms();

    // Message to encrypt
    unsigned char plaintext[] = "Hello, world!";

    // Length of the plaintext
    int plaintext_len = strlen((char *)plaintext);
    
    // Buffer for the ciphertext
    unsigned char *ciphertext = malloc(plaintext_len);

    printf("Plaintext: %s\n", plaintext);

    // Encryption
    xor_encrypt_decrypt(plaintext, secret, ciphertext, plaintext_len, secret_size);

    double encryption_time = get_time_ms() - encryption_start_time;

    printf("Ciphertext: ");
    for (int i = 0; i < plaintext_len; ++i) {
        printf("%02x", ciphertext[i]);
    }
    printf("\n");

    // Initialize connection
    {
        // Create socket
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            printf("\nSocket creation error \n");
            return -1;
        }
        
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(SERVER_PORT);
        // Convert string to IP address (local host)
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

    // Send the ciphertext to Bob
    send(sock, ciphertext, plaintext_len, 0);
    
    save_results_alice("alice_results.txt", plaintext, ciphertext, key_creation_time, encryption_time);

    // Free allocated memory
    free(ciphertext);
    free(secret);

    return 0;
}