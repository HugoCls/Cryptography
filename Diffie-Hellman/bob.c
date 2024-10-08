#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <openssl/dh.h>
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/bn.h>
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

void xor_encrypt_decrypt(unsigned char *input, unsigned char *key, unsigned char *output, int input_len, int key_len) {
    for (int i = 0; i < input_len; ++i) {
        output[i] = input[i] ^ key[i % key_len];
    }
}

DH *load_dh_params(const char *file_name) {
    DH *dh = NULL;
    FILE *param_file = fopen(file_name, "r");

    if (!param_file) {
        perror("Unable to open file with DH parameters");
        exit(EXIT_FAILURE);
    }

    dh = PEM_read_DHparams(param_file, NULL, NULL, NULL);
    fclose(param_file);

    if (!dh) {
        fprintf(stderr, "Error reading DH parameters from file\n");
        handleErrors();
    }
    
    if (1 != DH_generate_key(dh)) {
        handleErrors();
    }

    return dh;
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    DH *dh = NULL;
    BIGNUM *pub_key = NULL;
    const BIGNUM *pkey;

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

    // Loading DH parameters from a file
    dh = load_dh_params("dhparams.pem");

    DH_get0_key(dh, &pkey, NULL);
    pub_key = BN_dup(pkey);

    char *hex_pub_key = BN_bn2hex(pub_key);
    write(new_socket, hex_pub_key, strlen(hex_pub_key) + 1);
    printf("Bob sent his public key: %s\n", hex_pub_key);

    char alice_pub_key_hex[2048];
    int bytes_read = read(new_socket, alice_pub_key_hex, 2048);
    if (bytes_read < 0) {
        handleErrors();
    }
    
    printf("Bob received Alice's public key: %s\n", alice_pub_key_hex);

    BIGNUM *alice_pub_key = BN_new();
    if (!BN_hex2bn(&alice_pub_key, alice_pub_key_hex)) {
        handleErrors();
    }

    if (!alice_pub_key || BN_is_zero(alice_pub_key) || BN_is_negative(alice_pub_key)) {
        fprintf(stderr, "Invalid Alice's public key received.\n");
    
        BN_free(alice_pub_key);
        DH_free(dh);
        close(new_socket);
        exit(EXIT_FAILURE);
    }

    unsigned char *secret_buf = (unsigned char *)malloc(DH_size(dh));
    int secret_len = DH_compute_key(secret_buf, alice_pub_key, dh);
    if (secret_len <= 0) {
        handleErrors();
    }

    BIGNUM *secret_bn = BN_new();
    BN_bin2bn(secret_buf, secret_len, secret_bn);
    char *hex_secret = BN_bn2hex(secret_bn);
    printf("Shared secret: %s\n", hex_secret);

    close(new_socket);

    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
        perror("Accept");
        exit(EXIT_FAILURE);
    }

    // Lire le texte chiffré envoyé par Alice
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

    double decryption_start_time = get_time_ms();

    // Déchiffrer le texte chiffré
    unsigned char *decrypted_text = malloc(ciphertext_len);
    xor_encrypt_decrypt(ciphertext, secret_buf, decrypted_text, ciphertext_len, secret_len);
    decrypted_text[ciphertext_len] = '\0'; // Ajoute un null terminator
    double decryption_time = get_time_ms() - decryption_start_time;

    printf("Decrypted text: %s\n", decrypted_text);

    save_results_bob("bob_results.txt", decrypted_text, ciphertext, decryption_time);

    // Libérer la mémoire allouée
    free(decrypted_text);
    OPENSSL_free(hex_secret);
    BN_free(alice_pub_key);
    BN_free(secret_bn);
    free(secret_buf);
    DH_free(dh);
    close(new_socket);

    return 0;
}
